from loguru import logger

from etlclasses import ETLEnricherData, ETLProducerTable
from etldecorator import coroutine, some_sleep
from etlpostgres import ETLPG
from etlredis import ETLRedis
from etlsettings import ETLSettings


class ETLProducer:
    producer_table = [
        ETLProducerTable(table='djfilmwork', isrelation=False),
        ETLProducerTable(table='djfilmperson', field='film_work_id', ptable='djfilmworkperson', pfield='person_id'),
        ETLProducerTable(table='djfilmgenre', field='film_work_id', ptable='djfilmworkgenre', pfield='genre_id'),
        ETLProducerTable(table='djfilmtype', field='id', ptable='djfilmwork', pfield='type_id'),
    ]

    def __init__(self):
        cnf = ETLSettings()
        self.limit = cnf.etl_size_limit
        self.redis = ETLRedis()
        self.pgbase = ETLPG()

    def worker(self, producer):
        """
        Get List of ETLProducerTable and start etl process from django to redis, for each table.
        """
        while self.redis.get_status('producer') == 'run':
            for table in self.producer_table:
                logger.info(f'start processing : {table}')
                producer.send(table)

    @coroutine
    def producer(self, enricher):
        """
        This coroutine get modifed data from producer table, and send it to enricher.
        The state is stored in Redis.
        If no state in Redis, get all data from producer table.
        """
        while True:
            data: ETLProducerTable = (yield)
            lasttime = self.redis.get_lasttime(data.table) or self.pgbase.get_first_object_time(data.table)
            idlist = self.pgbase.get_updated_object_id(lasttime, data.table, self.limit)
            logger.info(f'get new or modifed data from postgress "{data.table}" table')
            try:
                lasttime = self.redis.set_lasttime(data.table, idlist[-1].modified)
            except IndexError:
                logger.warning(f'No more new data in {data.table}')
                some_sleep(min_sleep_time=1, max_sleep_time=10)
            idlist = [filmid.id for filmid in idlist]
            enricher.send(ETLEnricherData(data, idlist))

    @coroutine
    def enricher(self):
        """
        Get modified film id from main table.
        If table is main, simple get modifed film id.
        """
        while True:
            data: ETLEnricherData = (yield)
            logger.info(f'get film id modifed by {data.table.table} and store it in Redis')
            offset = 0
            isupdatedid = True if len(data.idlist) > 0 else False
            while isupdatedid:
                filmids = (
                    self.pgbase.get_updated_film_id(data.table, tuple(data.idlist), self.limit, offset)
                    if data.table.isrelation else data.idlist
                )
                [self.redis.push_filmid(id) for id in filmids]
                if (len(filmids) == self.limit) and (data.table.isrelation):
                    offset += self.limit
                else:
                    isupdatedid = False

    def start(self):
        if self.redis.get_status('producer') == 'run':
            logger.warning('ETL Producer already started, please stop it before run!')
            return
        else:
            self.redis.set_status('producer', 'run')

        enricher = self.enricher()
        producer = self.producer(enricher)
        self.worker(producer)

    def stop(self):
        self.redis.set_status('producer', 'stop')
        logger.info('producer stopped')


if __name__ == '__main__':
    ETLProducer().stop()
    ETLProducer().start()
