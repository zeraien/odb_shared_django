"""
Author: Me

A simple lockfile class used for concurrent access restriction.
A timeout can be given to make sure the lockfile expires.

"""

from builtins import str
from builtins import object
import os
import stat
import time
import datetime
import tempfile
import logging
import random
from odb_shared import get_logger

logger = get_logger("lockfile")

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
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("[%s] lockfile check starting in %ss" % (self.filename, sleep_sec))
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
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug("[%s] lockfile found, but timed out" % self.filename)
                    return False
                else:
                    return True
            except IOError:
                logger.warning("Error reading or writing to lockfile %s" % self.filename, exc_info=True)

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
                logger.exception("Failed to delete lockfile - this should not be happening!")
            finally:
                global lockfiles
                if self.filename in lockfiles:
                    del(lockfiles[self.filename])

    def get_lock_time(self):
        """Return the time when the lockfile was created."""
        return self.lock_time

    def __repr__(self):
        return self.filename
