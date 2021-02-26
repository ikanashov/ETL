import json
from dataclasses import asdict
from typing import List

from elasticsearch import Elasticsearch
from elasticsearch import TransportError

from loguru import logger

from etlclasses import ESMovie
from etldecorator import backoff
from etlsettings import ETLSettings


class ETLElastic:
    def __init__(self):
        cnf = ETLSettings()
        self.hosts = cnf.elastic_host
        self.port = cnf.elastic_port
        self.scheme = cnf.elastic_scheme
        self.http_auth = (cnf.elastic_user, cnf.elastic_password)
        self.index_name = cnf.elastic_index

        self.es = self.connect()

    def connect(self) -> Elasticsearch:
        return Elasticsearch(self.hosts, port=self.port, scheme=self.scheme, http_auth=self.http_auth)

    @backoff(start_sleep_time=0.5)
    def create_index(self, index_name='', index_body=''):
        try:
            self.es.indices.create(index_name, body=index_body)
        except TransportError as error:
            logger.warning(error)

    @backoff(start_sleep_time=0.5)
    def bulk_update(self, docs: List[ESMovie]) -> bool:
        if docs == []:
            logger.warning('No more data to update in elastic')
            return None
        body = ''
        for doc in docs:
            index = {'index': {'_index': self.index_name, '_id': doc.id}}
            body += json.dumps(index) + '\n' + json.dumps(asdict(doc)) + '\n'

        results = self.es.bulk(body)
        if results['errors']:
            error = [result['index'] for result in results['items'] if result['index']['status'] != 200]
            logger.debug(results['took'])
            logger.debug(results['errors'])
            logger.debug(error)
            return None
        return True
