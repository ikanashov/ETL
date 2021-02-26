from pydantic import BaseSettings


class ETLSettings(BaseSettings):
    postgres_db: str = 'postgres'
    postgres_host: str = 'localhost'
    postgres_port: int = 5432
    postgres_user: str = 'postgres'
    postgres_password: str = ''
    postgres_schema: str = 'public'
    redis_prefix: str = ''
    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_password: str = ''
    elastic_host: str = 'localhost'
    elastic_port: int = 9200
    elastic_scheme: str = 'http'
    elastic_user: str = 'elastic'
    elastic_password: str = ''
    elastic_index: str = 'movies'
    etl_size_limit: int = 10

    class Config:
        env_file = '../.env'
