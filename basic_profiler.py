import time

from django.conf import settings


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
            print(self.title, round(self.time_end-self.time_start, 4))


