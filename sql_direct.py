from django.conf import settings
from django.db import connection
from odb_shared import reraise, get_logger


def sql_update_with_key(table_name, primary_key, data_list):
    if not len(data_list):
        return

    keys = list(data_list[0].keys())
    _values_list = []
    for row in data_list:
        _values_list.append(tuple([row[k] for k in keys] + [row[primary_key]]))

    query = "UPDATE %(table_name)s SET %(update_q)s WHERE %(pk)s = %%s" % {
        'table_name': table_name,
        'update_q':  "=%s, ".join(keys) + "=%s",
        'pk': primary_key
    }

    cursor = connection.cursor()
    _values_list = list(set(_values_list))
    for v in _values_list:
        cursor.execute(query, v)
    cursor.close()

def sql_insert(table_name, data_list, single_query=False, update_if_exists=True):
    """
    *This function is a generator.*

    Insert multiple items into an SQL table.
    If `single_query` is True, simply returns nothing.
    If however `single_query` is False, it will return a generator with every new ID created by AUTO_INCREMENT.

    :param table_name:
    :param data_list: list of dictionaries with column:value to insert or update.
    :param single_query: Do all inserts in one query.
    :param update_if_exists: if entries already exist, they should be updated instead of there being an error
    :return:
    """
    if not len(data_list):
        return

    original_keys = list(data_list[0].keys())
    keys = ["`%s`"%k for k in original_keys]
    _values_list = []
    _values_count = len(keys)
    for row in data_list:
        _values_list.append(tuple([row[k] for k in original_keys]))

    values_placeholders = '(%s)' % ', '.join(["%s"] * _values_count)
    if single_query:
        values_placeholders = ','.join([values_placeholders] * len(_values_list))

    sql_replacement = {
        'table_name': table_name,
        'column_names': ",".join(keys),
        "values_placeholders": values_placeholders
    }

    if not update_if_exists or settings.DATABASES['default']['ENGINE'] == "django.db.backends.sqlite3":
        query = _sql_insert_command() % sql_replacement
    else:
        sql_replacement.update({
            'update_query': ', '.join(['%s=VALUES(%s)' % (k,k) for k in keys])
        })
        query = _sql_insert_command() % sql_replacement
        # for idx, v in enumerate(_values_list):
        #     _values_list[idx] = tuple(v + v)
    _values_list = list(set(_values_list))

    cursor = connection.cursor()
    try:
        if single_query:
            yield cursor.execute(query, [item for sublist in _values_list for item in sublist])
        else:
            for v in _values_list:
                cursor.execute(query, v)
                yield cursor.lastrowid
    except TypeError as e:
        get_logger().exception("Error in SQL Query for table: %s" % table_name, exc_info=1)
        reraise(e)
    cursor.close()

def _sql_insert_command():

    if settings.DATABASES['default']['ENGINE'] == "django.db.backends.sqlite3":
        return "INSERT INTO %(table_name)s (%(column_names)s) VALUES %(values_placeholders)s"
    else:
        return "INSERT INTO %(table_name)s (%(column_names)s) VALUES %(values_placeholders)s ON DUPLICATE KEY UPDATE %(update_query)s"
