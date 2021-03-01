import http.client
import os

from dotenv import load_dotenv

import psycopg2

from etlclasses import imdb_name_basics, imdb_to_postgres


class IMDBMovies:
    TSVTABLES = {
        'name_basics': 'db/name.basics.tsv',
        'title_basics': 'db/title.basics.tsv',
        'title_episode': 'db/title.episode.tsv',
    }
    SQLGETIMDBBYID = '''SELECT tb.tconst, te.parenttconst, tb.titletype, tb.primarytitle, tb.isadult,
                           tb.startyear, tb.endyear, te.seasonnumber, te.episodenumber
                        FROM imdb.title_basics as tb
                        LEFT JOIN imdb.title_episode as te on te.tconst = tb.tconst
                        WHERE tb.tconst = %s'''
    SQLGETPERSONBYNAME = 'SELECT * FROM imdb.name_basics WHERE primaryname = %s'

    def __init__(self, envfile='../.env'):
        dotenv_path = os.path.join(os.path.dirname(__file__), envfile)
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)

        self.conn = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB', 'postgres'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', ''),
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=int(os.getenv('POSTGRES_PORT', '5432')),
            options='-c search_path=' + os.getenv('POSTGRES_SCHEMA', 'public'),
        )

    def copy_to_table_from_csv(self, tablename: str, csvobject):
        """Copy data to tablename table.
        TRUNCATE table before copy data!
        """
        with self.conn as conn, conn.cursor() as cur:
            cur.execute('TRUNCATE ' + tablename)
            cur.copy_from(csvobject, tablename, sep='\t')

    def load_data_from_tsv(self):
        for table, filename in self.TSVTABLES.items():
            with open(filename) as tsvfile:
                # Read line with header
                tsvfile.readline()
                self.copy_to_table_from_csv(table, tsvfile)

    def get_imdb_id_by_https(self, imdb_tconst: str) -> str:
        conn = http.client.HTTPSConnection('www.imdb.com')
        conn.request('GET', f'/title/{imdb_tconst}/')
        response = conn.getresponse()
        if response.code == 301:
            dictheaders = [(value) for key, value in response.getheaders() if key == 'Location']
            url = dictheaders[0]
            imdb_tconst = url.split('/')[2]
            return imdb_tconst

    def pg_single_query(self, sqlquery: str, queryargs: tuple) -> tuple:
        with self.conn as conn, conn.cursor() as cur:
            cur.execute(sqlquery, queryargs)
            row = cur.fetchone()
        return row

    def pg_multy_query(self, sqlquery: str, queryargs: tuple) -> list:
        with self.conn as conn, conn.cursor() as cur:
            cur.execute(sqlquery, queryargs)
            rows = cur.fetchall()
        return rows

    def get_imdb_movie_by_id(self, movie_id: str) -> imdb_to_postgres:
        row = self.pg_single_query(self.SQLGETIMDBBYID, (movie_id,))
        if row:
            return imdb_to_postgres(*row)
        else:
            movie_id = self.get_imdb_id_by_https(movie_id)
            row = self.pg_single_query(self.SQLGETIMDBBYID, (movie_id,))
        if row:
            return imdb_to_postgres(*row)

    def get_imdb_person_by_name(self, person: str, role: str, movie_id: str) -> imdb_name_basics:
        names = self.pg_multy_query(self.SQLGETPERSONBYNAME, (person,))
        size = len(names)
        if size == 0:
            return None
        if size == 1:
            return imdb_name_basics(*names[0])
        for name in names:
            imdb_name = imdb_name_basics(*name)
            if (imdb_name.knownfortitles) and (movie_id in imdb_name.knownfortitles):
                return imdb_name_basics(*name)
        for name in names:
            imdb_name = imdb_name_basics(*name)
            if (imdb_name.primaryprofession) and (role[0:3] in imdb_name.primaryprofession):
                return imdb_name_basics(*name)
        for name in names:
            imdb_name = imdb_name_basics(*name)
            if imdb_name.birthyear:
                return imdb_name_basics(*name)
        for name in names:
            imdb_name = imdb_name_basics(*name)
            if imdb_name.knownfortitles:
                return imdb_name_basics(*name)


if __name__ == '__main__':
    pass
