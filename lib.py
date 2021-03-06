import hashlib
import warnings


def make_query_string_from_data(_max_length=191, **kwargs):
    if _max_length<100:
        raise AttributeError("The max_length for query string must be at least 100")

    def g(val):
        if isinstance(val, (list,tuple)):
            l = []
            for subval in val:
                print(subval)
                l.append(unicode(subval).encode('utf8'))
            l = ",".join(l)
            return "[%s]"%l
        return unicode(val).encode("utf8")
    if len(kwargs)==0:
        return None
    sorted_keys = sorted(kwargs.keys())
    v = u"&".join(["%s=%s"%(key, g(kwargs[key]).decode("utf8")) for key in sorted_keys])

    if len(v)>_max_length:
        tja = hashlib.sha1(v).hexdigest()
        ed = (_max_length - len(tja))
        return "%s-%s" % (v[0:ed-1],tja)
    else:
        return v
