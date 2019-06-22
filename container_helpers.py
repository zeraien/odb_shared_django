
def mklist(value):
    """
    Make a list from the provided value, if the value is not a list
    return a list with the value.
    If the value is an iterable it will be returned.
    Duplicate values are removed and the order is

    :param value: Any value or an iterable.
    :return:
    """
    try:
        if not isinstance(value, str):
            f = iter(value)
            return value
    except TypeError:
        pass
    return [value]

def enumerate_params(params):
    """
    Params should be a dictionary and the values are enumerated -
    if any of the values is a list, the same key is repeated multiple times
    for each value in the list.
    If the value is not a list, it simply enumerates once for that key.

    :param params: a dictionary
    :return: Does not return, it's a generator.
    """
    if type(params) is dict:
        for key, value in list(params.items()):
            for v in mklist(value):
                yield key, v
    else:
        yield None,None

