import logging
import time
import functools
from django.conf import settings
from django.utils.decorators import available_attrs

logger = logging.getLogger("odb.profiler")

class Profile(object):
    def __init__(self, title):
        self.title = title
        self.time_start = None
        self.time_end = None
    def __enter__(self):
        if settings.DEBUG and settings.PROFILE_PRINT_ENABLED:
            self.time_start = time.time()
    def __exit__(self, type, value, traceback):
        if settings.DEBUG and settings.PROFILE_PRINT_ENABLED:
            self.time_end = time.time()
            logger.debug("#### BASIC PROFILER #### %s - %s" % (self.title, "%ss" % round(self.time_end-self.time_start, 4)))


def profiler(func):
    @functools.wraps(func, assigned=available_attrs(func))
    def call(*args, **kwargs):
        with Profile(func.__name__):
            return func(*args, **kwargs)
    return call
