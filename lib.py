import hashlib
from functools import reduce


def make_query_string_from_data(_max_length=191, **kwargs):
    if _max_length<100:
        raise AttributeError("The max_length for query string must be at least 100")

    def g(val):
        if isinstance(val, (list,tuple)):
            l = []
            for subval in val:
                l.append(subval)
            l = ",".join(map(str,l))
            return "[%s]"%l
        return val
    if len(kwargs)==0:
        return None
    sorted_keys = sorted(kwargs.keys())
    v = u"&".join(["%s=%s"%(key, g(kwargs[key])) for key in sorted_keys])

    if len(v)>_max_length:
        tja = hashlib.sha1(v.encode("utf8")).hexdigest()
        ed = (_max_length - len(tja))
        return "%s-%s" % (v[0:ed-1],tja)
    else:
        return v
