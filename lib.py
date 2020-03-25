import hashlib

def make_query_string_from_data(max_length_=191, **kwargs):
    if max_length_<100:
        raise AttributeError("The max_length for query string must be at least 100")

    def g(val):
        if isinstance(val, (list,tuple)):
            l = []
            for subval in val:
                print(subval)
                l.append(unicode(subval).encode('utf8'))
            l = ",".join(l)
            return "[%s]"%l
        return str(val).encode("utf8")
    if len(kwargs)==0:
        return None
    sorted_keys = sorted(kwargs.keys())
    v = "&".join(["%s=%s"%(key, g(kwargs[key])) for key in sorted_keys])

    if len(v)>max_length_:
        tja = hashlib.sha1(v).hexdigest()
        ed = (max_length_ - len(tja))
        return "%s-%s" % (v[0:ed-1],tja)
    else:
        return v
