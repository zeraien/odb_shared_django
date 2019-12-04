from future.utils import raise_with_traceback

from .container_helpers import multikeysort, dict_from_list, slice_generator, group_by_key

__author__ = 'zeraien'

import logging
import sys

def get_logger(extra_funnel=None):
    funnel = 'odb'
    if extra_funnel:
        funnel = '.'.join((funnel,extra_funnel))
    return logging.getLogger(funnel)

def reraise(exception):
    raise_with_traceback(exception)
