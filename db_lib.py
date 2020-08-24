from typing import Iterable, Union, Dict, Any, Sized

from .container_helpers import mklist

def get_query_for_data_pairs(
        data_pairs:Iterable[Iterable],
        id_param_name:str,
        table_name:str,
        limit_to_ids:Iterable[Union[str,int]]=None) -> (str,Dict[str,Any]):
    """
    When storing data with name/value pairs, if you need to retrieve a grouping of name/value
    pairs, use this.
    Meaning you have key/value columns, like so:
    id | key | value | parent_id
     #   foo   bar        1
     #   foo   baz        2
     #   user   3         1
     #   user   4         2

    If you wish to retrieve certain pairings, like you want all user=3 AND foo=baz, you'll get a
    query that will get you the list of all parent id's matching that. In the example above, it's [1].

    :param data_pairs: a list of data pair lists `[[key,value],....]`
    :param id_param_name: the name of the id column for the parent table
    :param table_name: table name of the key/value pair table
    :param limit_to_ids: limit the query to the parent ids
    :returns : the database query with one `id` column being the `id` of the entries in the parent table and a dictionary with the values.
    :raises ValueError: if invalid data pair is supplied
    """

    tables = []
    wheres = []
    value_list = {}
    if limit_to_ids:
        wheres.append("D0.{id_param_name} IN (%s)" % ",".join(["%%(id%s)s"%i for i,s in enumerate(range(len(limit_to_ids)))]))
        value_list.update({"id%s"%i:s for i,s in enumerate(limit_to_ids)})

    for index, data_pair in enumerate(data_pairs, start=0):
        if not isinstance(data_pair, (list,tuple)):
            raise ValueError("Data should be in the format [[k,v],...]")
        key, value = data_pair[0],data_pair[1]
        # if issubclass(value.__class__,'hashid_field.Hashid'):
        #     value = int(value)
        prefix = "D%s"%index
        if index>0:
            on = "ON D%s.{id_param_name} = D%s.{id_param_name}" % (index-1, index)
        else:
            on = ""
        tables.append("%(table)s as %(prefix)s %(on)s" % {
            'on':on,
            'table':table_name,
            "prefix":prefix
        })
        _value_list = mklist(value)
        if len(_value_list):
            wheres.append("""(%(prefix)s.key=%(key)s AND %(prefix)s.value IN (%(val)s))""" % {
                "prefix":prefix,
                "key": "%%(key%s)s"%index,
                "val": ','.join(["%%(val%s.%s)s"%(index,i) for i,v in enumerate(range(len(_value_list)))])
            })
            value_list['key%s'%index] = key
            value_list.update({"val%s.%s"%(index,i):s for i,s in enumerate(_value_list)})

    #py3
    wheres_str = len(wheres) and ("WHERE %s" % " AND ".join(wheres).strip()) or ""
    query = ("""
    SELECT D0.{id_param_name} as `id`
     FROM %(from)s
     %(where)s
     GROUP BY D0.{id_param_name}
      ORDER BY D0.{id_param_name}""" %
    {'from': " LEFT JOIN ".join(tables).strip(),
     'where': wheres_str}).format(**{'id_param_name': id_param_name})
    q,v = " ".join([line.strip() for line in query.strip().splitlines()]), value_list
    return q,v
