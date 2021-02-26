from typing import List

from loguru import logger

from esindex import CINEMA_INDEX_BODY as esbody
from etlclasses import ESMovie, ESPerson, ETLFilmWork
from etldecorator import coroutine, some_sleep
from etlelastic import ETLElastic
from etlpostgres import ETLPG
from etlredis import ETLRedis
from etlsettings import ETLSettings


class ETLConsumer:

    def __init__(self):
        cnf = ETLSettings()

        self.index_name = cnf.elastic_index
        self.limit = cnf.etl_size_limit

        self.redis = ETLRedis()
        self.pgbase = ETLPG()
        self.es = ETLElastic()

    def get_filmsid_from_redis(self, putter) -> List[ETLFilmWork]:
        while self.redis.get_status('consumer') == 'run':
            idlists = self.redis.get_filmid_for_work(self.limit)
            films = self.pgbase.get_filmsbyid(tuple(idlists)) if len(idlists) > 0 else []
            putter.send(films)

    @coroutine
    def put_films_to_ES(self) -> bool:
        while True:
            films: List[ETLFilmWork] = (yield)
            logger.info('Start loading data to elastic')
            esfilms = [
                ESMovie(
                    film.id, film.rating, film.imdb_tconst, film.type_name, film.genres,
                    film.title, film.description,
                    [name.split(' : ')[1] for name in film.directors] if film.directors else None,
                    [name.split(' : ')[1] for name in film.actors] if film.actors else None,
                    [name.split(' : ')[1] for name in film.writers] if film.writers else None,
                    [ESPerson(*name.split(' : ')) for name in film.directors] if film.directors else None,
                    [ESPerson(*name.split(' : ')) for name in film.actors] if film.actors else None,
                    [ESPerson(*name.split(' : ')) for name in film.writers] if film.writers else None
                ) for film in films]
            if self.es.bulk_update(esfilms):
                self.redis.del_work_queuename()
                logger.info('Data succesfully loaded, delete working queue')
            else:
                some_sleep(min_sleep_time=1, max_sleep_time=10)

    def start(self):
        if self.redis.get_status('consumer') == 'run':
            logger.warning('ETL Consumer already started, please stop it before run!')
            return
        else:
            self.redis.set_status('consumer', 'run')
            self.es.create_index(self.index_name, esbody)

        putter = self.put_films_to_ES()
        self.get_filmsid_from_redis(putter)

    def stop(self):
        self.redis.set_status('consumer', 'stop')
        logger.info('consumer stopped')


if __name__ == '__main__':
    ETLConsumer().stop()
    ETLConsumer().start()
