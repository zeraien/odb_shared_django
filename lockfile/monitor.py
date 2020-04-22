"""
Author: Me

A simple lockfile class used for concurrent access restriction.
A timeout can be given to make sure the lockfile expires.

"""

try:
    from contextlib import ContextDecorator
except ImportError:
    #python 2.7 and django<2 compat
    from django.utils.decorators import ContextDecorator

from django.utils.encoding import smart_str as smart_text
import time
import logging
import hashlib
from odb_shared import get_logger
from .exceptions import LockfileExistsException
from . import RedisLock

logger = get_logger("lockfile")

#todo rename to Semaphore, since that's what this is?
class Monitor(ContextDecorator):
    """This class is used as such:

    with Monitor(data=(list_of_items), timeout=??):
        do some stuff that should be thread-safe

    Until the stuff within the `with` statement completes,
     the monitor will block execution, but only if the `list_of_items` is
     identical to an already running Monitor.

     If `with` statement is used with the `as` operator, the returned value is whether the
     monitor was initially locked. This is useful if you do not want to repeat a long running
     operation that just completed.

     If passing `raise_if_already_locked`, the monitor will raise `LockfileExistsException` if
     the lockfile already exists when this monitor is poked.
    """
    def __init__(self, name, data, timeout=180, raise_if_already_locked=False, lockfile_klass=RedisLock):

        if timeout is None: timeout = 0

        self.timeout = timeout
        self.running_time = 0.
        self.raise_if_already_locked = raise_if_already_locked
        self.name = name
        self.digest = hashlib.sha1((smart_text(data) + name).encode("utf8")).hexdigest() + '-' + smart_text(name)
        self.lockfile = lockfile_klass(self.digest, timeout=timeout)


    def __enter__(self):

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Monitor [%s] check starting... [%s]" % (self.name, self.digest))

        was_locked_initially = lockfile_exists = self.lockfile.exists()

        if was_locked_initially and self.raise_if_already_locked:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Monitor [%s] lockfile found" % self.name)
            raise LockfileExistsException("[%s] already locked with [%s], bailing out."% (self.name,self.lockfile))

        interval = 0.5

        while lockfile_exists and (self.timeout > 0 and self.running_time <= self.timeout):
            self.running_time += interval
            time.sleep(interval)
            lockfile_exists = self.lockfile.exists()

        self.lockfile.create()
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Monitor [%s] is green!" % (self.name, ))

        return was_locked_initially

    def __exit__(self, type, value, traceback):
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Monitor [%s] activity is finished!" % (self.name, ))
        self.lockfile.delete()
