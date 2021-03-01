import io
import os

from dotenv import load_dotenv

import psycopg2


class DJNewMovies:

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

    def copy_to_csv_from_table(self, tablename: str) -> io.StringIO:
        csvtable = io.StringIO()
        with self.conn as conn, conn.cursor() as cur:
            cur.copy_to(csvtable, tablename, sep='|')
        csvtable.seek(0)
        return csvtable

    def copy_to_table_from_csv(self, tablename: str, csvtable: io.StringIO):
        with self.conn as conn, conn.cursor() as cur:
            cur.copy_from(csvtable, tablename, sep='|')
