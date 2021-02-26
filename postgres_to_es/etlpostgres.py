from datetime import datetime, timedelta
from typing import List

from psycopg2 import connect as pgconnect, sql

from etlclasses import ETLFilmWork, ETLModifiedID, ETLProducerTable
from etldecorator import backoff
from etlsettings import ETLSettings


class ETLPG:
    FIRSTTIME = 'SELECT modified FROM {} ORDER BY modified LIMIT 1'
    UPDATED = 'SELECT id, modified FROM {} WHERE modified  > %s ORDER BY modified LIMIT %s'
    FILMUPDATED = 'SELECT DISTINCT {field} FROM {ptable} WHERE {pfield} in %s ORDER BY {field} LIMIT %s OFFSET %s'
    GETFILMSBYID = '''
    SELECT
        fw.id, fw.rating, fw.imdb_tconst, ft.name,
        ARRAY_AGG(DISTINCT fg.name ) AS genres,
        fw.title, fw.description,
        ARRAY_AGG(DISTINCT fp.id || ' : ' || fp.full_name) FILTER (WHERE fwp.role = 'director') AS directors,
        ARRAY_AGG(DISTINCT fp.id || ' : ' || fp.full_name) FILTER (WHERE fwp.role = 'actor') AS actors,
        ARRAY_AGG(DISTINCT fp.id || ' : ' || fp.full_name) FILTER (WHERE fwp.role = 'writer') AS writers,
        fw.modified
    FROM djfilmwork AS fw
    LEFT OUTER JOIN djfilmworkperson AS fwp ON fw.id = fwp.film_work_id
    LEFT OUTER JOIN djfilmperson AS fp ON fwp.person_id = fp.id
    LEFT OUTER JOIN djfilmworkgenre AS fwg ON fw.id = fwg.film_work_id
    LEFT OUTER JOIN djfilmgenre AS fg ON fwg.genre_id = fg.id
    INNER JOIN djfilmtype AS ft ON fw.type_id = ft.id
    WHERE fw.id IN %s
    GROUP BY fw.id, ft.id
    '''

    def __init__(self):
        self.cnf = ETLSettings()
        self.conn = self.connect()

    @backoff(start_sleep_time=0.1)
    def connect(self):
        return pgconnect(
            dbname=self.cnf.postgres_db,
            user=self.cnf.postgres_user,
            password=self.cnf.postgres_password,
            host=self.cnf.postgres_host,
            port=self.cnf.postgres_port,
            options='-c search_path=' + self.cnf.postgres_schema,
        )

    @backoff(start_sleep_time=0.1)
    def pg_single_query(self, sqlquery: str, queryargs: tuple) -> tuple:
        self.conn = self.connect() if self.conn.closed != 0 else self.conn
        with self.conn as conn, conn.cursor() as cur:
            cur.execute(sqlquery, queryargs)
            row = cur.fetchone()
        return row

    @backoff(start_sleep_time=0.1)
    def pg_multy_query(self, sqlquery: str, queryargs: tuple) -> list:
        self.conn = self.connect() if self.conn.closed != 0 else self.conn
        with self.conn as conn, conn.cursor() as cur:
            cur.execute(sqlquery, queryargs)
            rows = cur.fetchall()
        return rows

    def get_first_object_time(self, table: str) -> datetime:
        """
        If redis store is clean, get time of first object in table.
        Then subtract one millisecond, because >, not >=
        """
        query = sql.SQL(self.FIRSTTIME).format(sql.Identifier(table))
        time = self.pg_single_query(query, None)[0] - timedelta(0, 0, 0, 1)
        return time

    def get_updated_object_id(self, lasttime: datetime, table: str, limit: int) -> List[ETLModifiedID]:
        query = sql.SQL(self.UPDATED).format(sql.Identifier(table))
        idlists = [ETLModifiedID(*id) for id in self.pg_multy_query(query, (lasttime, limit, ))]
        return idlists

    def get_updated_film_id(self, producer: ETLProducerTable, idlists: tuple, limit: int, offset: int) -> list:
        query = sql.SQL(self.FILMUPDATED).format(
            field=sql.Identifier(producer.field),
            ptable=sql.Identifier(producer.ptable),
            pfield=sql.Identifier(producer.pfield)
        )
        filmids = [id for (id,) in self.pg_multy_query(query, (idlists, limit, offset, ))]
        return filmids

    def get_filmsbyid(self, idlists: tuple) -> List[ETLFilmWork]:
        films = [ETLFilmWork(*row) for row in self.pg_multy_query(self.GETFILMSBYID, (idlists,))]
        return films
