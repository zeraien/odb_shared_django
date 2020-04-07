from .container_helpers import mklist

def get_query_for_data_pairs(data_pairs, id_param_name, table_name, limit_to_ids=None):
    """
    When storing data with name/value pairs, if you need to retrieve a grouping of name/value
    pairs, use this.

    :param list[list or tuple[str,Any]] data_pairs: a list of data pair lists `[[key,value],....]`
    :param str id_param_name: the name of the id column for the parent table
    :param str table_name: table name of the key/value pair table
    :param list[int] limit_to_ids: limit the query to the parent ids
    :returns (str,dict): the database query with one `id` column being the `id` of the entries in the parent table and a dictionary with the values.
    """

    tables = []
    wheres = []
    value_list = {}
    if limit_to_ids:
        wheres.append("D0.%%(id_param_name)s IN (%s)" % ",".join(["%%%%(id%s)s"%i for i,s in enumerate(range(len(limit_to_ids)))]))
        value_list.update({"id%s"%i:s for i,s in enumerate(limit_to_ids)})

    for index, data_pair in enumerate(data_pairs, start=0):
        if not isinstance(data_pair, (list,tuple)):
            raise ValueError("Data should be in the format [[k,v],...]")
        key, value = data_pair[0],data_pair[1]
        # if issubclass(value.__class__,'hashid_field.Hashid'):
        #     value = int(value)
        prefix = "D%s"%index
        if index>0:
            on = "ON D%s.%%(id_param_name)s = D%s.%%(id_param_name)s" % (index-1, index)
        else:
            on = ""
        tables.append("%(table)s as %(prefix)s %(on)s" % {
            'on':on,
            'table':table_name,
            "prefix":prefix
        })
        _value_list = mklist(value)
        wheres.append("""(%(prefix)s.key=%(key)s AND %(prefix)s.value IN (%(val)s))""" % {
            "prefix":prefix,
            "key": "%%%%(key%s)s"%index,
            "val": ','.join(["%%%%(val%s.%s)s"%(index,i) for i,v in enumerate(range(len(_value_list)))])
        })
        value_list['key%s'%index] = key
        value_list.update({"val%s.%s"%(index,i):s for i,s in enumerate(_value_list)})
    #py3
    wheres_str = " AND ".join(wheres).strip()
    query = """
    SELECT D0.%%(id_param_name)s as `id`
     FROM %(from)s WHERE 
     %(where)s
     GROUP BY D0.%%(id_param_name)s
      ORDER BY D0.%%(id_param_name)s""" %\
    {'from': " LEFT JOIN ".join(tables).strip(),
     'where': wheres_str} % {'id_param_name': id_param_name}
    return " ".join([line.strip() for line in query.strip().splitlines()]), value_list
