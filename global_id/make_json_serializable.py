""" Module that monkey-patches json module when it's imported so
JSONEncoder.default() automatically checks for a special "to_json()"
method and uses it to encode the object if found.
"""
from datetime import datetime, date
from decimal import Decimal
from json import JSONEncoder

from django.conf import settings
from hashid_field import Hashid

from odb_shared.time_helpers import to_epoch


def _default(self, obj):
    if issubclass(obj.__class__, Hashid):
        return str(obj)
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, datetime):
        return to_epoch(obj)
    elif isinstance(obj, date):
        return obj.strftime(settings.PY_DATE_FORMAT)

    return _default.default(obj)

_default.default = JSONEncoder.default  # Save unmodified default.
JSONEncoder.default = _default # Replace it.
