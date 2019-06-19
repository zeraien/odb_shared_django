"""
Author: Me

A simple lockfile class used for concurrent access restriction.
A timeout can be given to make sure the lockfile expires.

"""
from __future__ import unicode_literals
from builtins import str
from builtins import object
import atexit

from django.utils.decorators import ContextDecorator
from django.utils.encoding import smart_text
import os
import stat
import time
import datetime
import tempfile
import logging
import random
import hashlib
from odb_shared import get_logger


class LockfileExistsException(Exception): pass

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
    def __init__(self, name, data, timeout=60, raise_if_already_locked=False):

        if timeout is None: timeout = 0

        self.timeout = timeout
        self.running_time = 0
        self.raise_if_already_locked = raise_if_already_locked
        self.name = name
        self.digest = hashlib.sha1(smart_text(data) + name).hexdigest() + '-' + smart_text(name)
        self.lockfile = Lockfile(self.digest, timeout=timeout)


    def __enter__(self):

        get_logger().debug("Monitor [%s] check starting... [%s]" % (self.name, self.digest))

        was_locked_initially = lockfile_exists = self.lockfile.exists()

        if was_locked_initially and self.raise_if_already_locked:
            get_logger().debug("Monitor [%s] lockfile found" % self.name)
            raise LockfileExistsException("[%s] already locked with [%s], bailing out."% (self.name,self.lockfile))

        while lockfile_exists and (self.timeout > 0 and self.running_time <= self.timeout):
            self.running_time += 1
            time.sleep(1)
            lockfile_exists = self.lockfile.exists()

        self.lockfile.create()
        get_logger().debug("Monitor [%s] is green!" % (self.name, ))

        return was_locked_initially

    def __exit__(self, type, value, traceback):
        get_logger().debug("Monitor [%s] activity is finished!" % (self.name, ))
        self.lockfile.delete()



class Lockfile(object):
    """A simple lockfile class with a timer, lockfile expires after the set timeout."""
    def __init__(self, filename, timeout=None):
        """
        Parameters:

        - `filename`: a filename for this lockfile, it will be created in a temp directory.
        - `timeout`: a timeout in seconds, if 0 or None, lockfile will never expire.
        """
        self.basename = filename
        self.filename = os.path.join(tempfile.gettempdir(), filename)
        self.timeout = timeout
        self.lock_time = datetime.datetime.fromtimestamp(0)

    def exists(self):
        """Return True if the lockfile exists. Call this before creating the lockfile!"""

        lock_file = self.filename

        sleep_sec = random.random() * .1
        get_logger().debug("[%s] lockfile check starting in %ss" % (self.filename, sleep_sec))
        time.sleep(sleep_sec)

        if os.path.exists(lock_file):
            if self.timeout is None or self.timeout <= 0:
                return True

            try:
                f_ = open(lock_file, 'r')
                _epoch = f_.readline(30).strip()

                if _epoch == '':
                    _time = datetime.datetime.now()
                else:
                    _time = datetime.datetime.fromtimestamp(float(_epoch))

                f_.close()
                self.lock_time = _time
                delta = datetime.timedelta(seconds=self.timeout)
                if _time + delta < datetime.datetime.now():
                    self.lock_time = datetime.datetime.fromtimestamp(0)
                    self.delete()
                    get_logger().debug("[%s] lockfile found, but timed out" % self.filename)
                    return False
                else:
                    return True
            except IOError:
                get_logger().warning("Error reading or writing to lockfile %s" % self.filename, exc_info=True)

                return False
        return False

    def create(self):
        """Create the lockfile. This should be run when the protected operation is starting, after calling `exists`."""
        timestamp = time.time()
        self.lock_time = datetime.datetime.fromtimestamp(timestamp)
        f_ = open(self.filename, 'w')
        f_.write(str(timestamp))
        os.chmod(self.filename, stat.S_IRUSR|stat.S_IWUSR|stat.S_IROTH|stat.S_IWOTH|stat.S_IWGRP|stat.S_IRGRP)
        f_.close()

        global lockfiles
        lockfiles[self.filename] = self

    def delete(self):
        """Delete the lockfile. This should be run when the protected operation is completed."""
        if os.path.exists(self.filename):
            try:
                os.unlink(self.filename)
            except OSError as e:
                get_logger().exception("Failed to delete lockfile - this should not be happening!")
            finally:
                global lockfiles
                if self.filename in lockfiles:
                    del(lockfiles[self.filename])

    def get_lock_time(self):
        """Return the time when the lockfile was created."""
        return self.lock_time

    def __repr__(self):
        return self.filename



def lockfile_wait(name, raise_if_already_locked=True, timeout=60):
    # Bare decorator: @lockfile_wait -- although the first argument is called
    # `name_or_func`, it's actually the function being decorated.
    name_or_func = name
    if callable(name_or_func):
        data = [name_or_func.__module__,name_or_func.__name__]
        return Monitor(name=".".join(data),
                       raise_if_already_locked=raise_if_already_locked,
                       data=data,
                       timeout=timeout)(name_or_func)
    # Decorator: @lockfile_wait(...) or context manager: with lockfile_wait(...): ...
    else:
        return Monitor(name=name_or_func,
                       raise_if_already_locked=raise_if_already_locked,
                       data=[name_or_func],
                       timeout=timeout)

lockfiles = {}

def cleanup():
    for lockfile in lockfiles.values():
        lockfile.delete()

atexit.register(cleanup)
