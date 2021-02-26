import random
from functools import wraps
from time import sleep

from loguru import logger


def coroutine(coro):
    @wraps(coro)
    def coroinit(*args, **kwargs):
        fn = coro(*args, **kwargs)
        next(fn)
        return fn
    return coroinit


def _sleep_time(start_sleep_time: float, border_sleep_time: float, factor: int, attempt: int, jitter: bool) -> float:
    try:
        sleep_time = (
            random.uniform(start_sleep_time, start_sleep_time * factor) * factor ** attempt if jitter
            else start_sleep_time * factor ** attempt)
    except OverflowError:
        logger.warning('Overflow in (factor ** attemt), sleep_time will be set to border_sleep_time')
        sleep_time = border_sleep_time
    return min(border_sleep_time, sleep_time)


def backoff(start_sleep_time=0.1, border_sleep_time=30, factor=2, jitter=True):
    """
    start_sleep_time - time for wich all backoff process always will be sleep
    border_sleep_time - maximum time wich procces will be wait, if service will not answer
    factor - factor to multiply wait time
    jitter - if True, proccess will be sleep random time between start_sleep_time and start_sleep_time * factor
    """
    if start_sleep_time < 0.001:
        logger.warning('start_sleep_time fewer than 0.001 and will be set to 0.001')
        start_sleep_time = 0.001

    def decorator(target):
        @wraps(target)
        def retry(*args, **kwargs):
            attempt = 0
            while True:
                sleep_time = _sleep_time(start_sleep_time, border_sleep_time, factor, attempt, jitter)
                try:
                    attempt += 1
                    sleep(sleep_time)
                    ret = target(*args, **kwargs)
                except Exception as e:
                    logger.error(f'Exception is catched {e}')
                    logger.warning(f'Wait fo {sleep_time} seconds and try again')
                else:
                    return ret
        return retry
    return decorator


def some_sleep(min_sleep_time=1, max_sleep_time=30):
    time = random.uniform(min_sleep_time, max_sleep_time)
    logger.info(f'the etl process will sleep {time} seconds.')
    sleep(time)
