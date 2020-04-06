""" Module that monkey-patches json module when it's imported so
JSONEncoder.default() automatically checks for a special "to_json()"
method and uses it to encode the object if found.
"""
from decimal import Decimal
from json import JSONEncoder
from hashid_field import Hashid

def _default(self, obj):
    if issubclass(obj.__class__, Hashid):
        return str(obj)
    elif isinstance(obj, Decimal):
        return float(obj)

    return _default.default(obj)

_default.default = JSONEncoder.default  # Save unmodified default.
JSONEncoder.default = _default # Replace it.
