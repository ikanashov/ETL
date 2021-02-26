from datetime import datetime

from redis import Redis

from etldecorator import backoff

from etlsettings import ETLSettings


class ETLRedis:
    def __init__(self):
        cnf = ETLSettings()
        self.prefix = cnf.redis_prefix + ':'
        self.queuename = self.prefix + 'filmids'
        self.workqueuename = self.queuename + ':work'

        self.redis = Redis(
            host=cnf.redis_host,
            port=cnf.redis_port,
            password=cnf.redis_password,
            decode_responses=True,
        )

    @backoff(start_sleep_time=0.001, jitter=False)
    def set_status(self, service: str, status: str) -> str:
        key = self.prefix + 'status:' + service
        self.redis.set(key, status)
        return self.redis.get(key)

    @backoff(start_sleep_time=0.001, jitter=False)
    def get_status(self, service: str) -> str:
        key = self.prefix + 'status:' + service
        return self.redis.get(key)

    @backoff(start_sleep_time=0.001, jitter=False)
    def set_lasttime(self, table: str, lasttime: datetime) -> datetime:
        key = self.prefix + table + ':lasttime'
        self.redis.set(key, lasttime.isoformat())
        time = self.redis.get(key)
        return datetime.fromisoformat(time)

    @backoff(start_sleep_time=0.001, jitter=False)
    def get_lasttime(self, table: str) -> datetime:
        key = self.prefix + table + ':lasttime'
        time = self.redis.get(key)
        return time

    @backoff(start_sleep_time=0.001, jitter=False)
    def push_filmid(self, id: str) -> str:
        """
        Attomic unique push film id in Redis queue
        """
        script = 'redis.call("LREM",KEYS[1], "0", ARGV[1]);'
        script += 'return redis.call("LPUSH", KEYS[1], ARGV[1])'
        self.redis.eval(script, 1, self.queuename, id)

    @backoff(start_sleep_time=0.001, jitter=False)
    def get_filmid_for_work(self, size) -> list:
        """
        Move film id from queue to workqueue to load or update it in elastic
        """
        size -= self.redis.llen(self.workqueuename)
        while size > 0:
            self.redis.rpoplpush(self.queuename, self.workqueuename)
            size -= 1
        len = self.redis.llen(self.workqueuename)
        workid = self.redis.lrange(self.workqueuename, 0, len)
        return workid

    @backoff(start_sleep_time=0.001, jitter=False)
    def del_work_queuename(self):
        self.redis.delete(self.workqueuename)
