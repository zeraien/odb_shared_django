"""
Author: Me

A simple lockfile class used for concurrent access restriction.
A timeout can be given to make sure the lockfile expires.

"""

from builtins import str
from builtins import object
import atexit

import redis
from django.conf import settings

try:
    from contextlib import ContextDecorator
except ImportError:
    #python 2.7 and django<2 compat
    from django.utils.decorators import ContextDecorator

from django.utils.encoding import smart_str as smart_text
import os
import stat
import time
import datetime
import tempfile
import logging
import random
import hashlib
from odb_shared import get_logger
from django.core.cache import cache

logger = get_logger("lockfile")

class CacheLock(object):
    def __init__(self, filename, timeout=None):
        self.basename = filename
        self.timeout = timeout
        self.lock_time = datetime.datetime.fromtimestamp(0)

    def exists(self):
        sleep_sec = random.random() * .1
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("[%s] lockfile check starting in %ss" % (self.basename, sleep_sec))
        time.sleep(sleep_sec)
        return cache.get(self.basename) is not None
    def create(self):
        timestamp = time.time()
        self.lock_time = datetime.datetime.fromtimestamp(timestamp)
        cache.set(self.basename, str(timestamp), self.timeout)
    def delete(self):
        cache.delete(self.basename)
    def get_lock_time(self):
        return self.lock_time
    def __repr__(self):
        return self.basename
