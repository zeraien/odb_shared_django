from collections import OrderedDict
from functools import cmp_to_key


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
            iter(value)
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


def group_by_key(iterable, keyfunc):
    grouped =  OrderedDict()
    for item in iterable:
        key = keyfunc(item)
        items_in_group = grouped.get(key, [])
        items_in_group.append(item)
        grouped[key] = items_in_group
    return grouped


def slice_generator(items, group_size):
    items_iter = iter(items)
    if group_size < 1:
        raise ValueError('group_size must be larger than 0')
    while True:
        out = []
        try:
            for i in range(0, group_size):
                out.append(next(items_iter))
        finally:
            if out:
                yield out

def dict_from_list(the_list, key):
    the_dict = {}
    key = str(key)

    for item in the_list:
        is_dict = type(item) is dict
        if is_dict:
            the_dict[item[key]] = item
        else:
            the_dict[getattr(item,key)] = item
    return the_dict

def _cmp(x, y):
    """
    Replacement for built-in function cmp that was removed in Python 3

    Compare the two objects x and y and return an integer according to
    the outcome. The return value is negative if x < y, zero if x == y
    and strictly positive if x > y.
    """

    return (x > y) - (x < y)

#http://stackoverflow.com/a/1144405/144838
def multikeysort(items, columns):
    """
    Sort a list of dicts on all given columns, in the order of the columns.
    :param items:
    :param columns: A list of columns to sort on, if a column starts with `-`, it should be sorted in reverse.
    :return: sorted `dict`
    """
    from operator import itemgetter
    comparers = [ ((itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1)) for col in columns]
    def comparer(left, right):
        for get_value, mult in comparers:
            result = _cmp(get_value(left), get_value(right))
            if result:
                return mult * result
        else:
            return 0
    return sorted(items, key=cmp_to_key(comparer))
