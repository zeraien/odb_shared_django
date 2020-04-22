"""
Author: Me

A simple lockfile class used for concurrent access restriction.
A timeout can be given to make sure the lockfile expires.

"""
from builtins import str
from builtins import object
import redis
from django.conf import settings
import time
import datetime
from django.core.cache import cache

class RedisLock(object):

    def __init__(self, filename, timeout=None):
        self.basename = filename
        self.timeout = timeout
        self.lock_time = datetime.datetime.fromtimestamp(0)
        self.redis_connection = redis.Redis(connection_pool=settings.REDIS_POOL)
        self.lock = self.redis_connection.lock(
            "odb_shared-lockfile-%s"%filename,
            timeout=timeout,
            blocking_timeout=timeout
        )

    def exists(self):
        return self.lock.locked()

    def create(self):
        self.lock.acquire(blocking=False)
        timestamp = time.time()
        self.lock_time = datetime.datetime.fromtimestamp(timestamp)

    def delete(self):
        if self.lock.locked():
            self.lock.release()
    def get_lock_time(self):
        return self.lock_time

    def __str__(self):
        return str(self.lock)

