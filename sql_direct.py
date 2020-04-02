import datetime

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

def sql_insert(table_name, data_list, single_query=False, update_if_exists=True, unique_keys=None):
    """
    *This function is a generator.*

    Insert multiple items into an SQL table.
    If `single_query` is True, simply returns nothing.
    If however `single_query` is False, it will return a generator with every new ID created by AUTO_INCREMENT.

    :param unique_keys: a list of columns that are unique, this is used for upserting with SQLite (which is used for testing)
    :param table_name:
    :param data_list: list of dictionaries with column:value to insert or update.
    :param single_query: Do all inserts in one query.
    :param update_if_exists: if entries already exist, they should be updated instead of there being an error
    :return:
    """
    TIME_FORMAT = '%H:%M'
    DATE_FORMAT = '%Y-%m-%d'
    DATETIME_FORMAT  = '%Y-%m-%d %H:%M:%S'
    if not len(data_list):
        return

    def _fix_value(value):
        if isinstance(value, datetime.datetime):
            return value.strftime(DATETIME_FORMAT)
        elif isinstance(value, datetime.time):
            return value.strftime(TIME_FORMAT)
        elif isinstance(value, datetime.date):
            return value.strftime(DATE_FORMAT)
        else:
            return value

    is_sqlite = settings.DATABASES['default']['ENGINE'] == "django.db.backends.sqlite3"
    original_keys = list(data_list[0].keys())
    keys = ["`%s`"%k for k in original_keys]
    _values_list = []
    _values_count = len(keys)
    for row in data_list:
        _values_list.append(tuple([_fix_value(row[k]) for k in original_keys]))

    values_placeholders = '(%s)' % ', '.join(["%s"] * _values_count)
    if single_query:
        values_placeholders = ','.join([values_placeholders] * len(_values_list))

    sql_replacement = {
        'table_name': table_name,
        'column_names': ",".join(keys),
        "values_placeholders": values_placeholders
    }
    do_update_if_exists = (
            update_if_exists
            and
            (
                    (
                            unique_keys and len(unique_keys)
                            and is_sqlite
                    )
                    or not is_sqlite
            )
    )

    query = _sql_insert_command(on_duplicate_update=do_update_if_exists,
                                unique_keys=unique_keys)
    if not do_update_if_exists:
        query = query % sql_replacement
    else:
        if is_sqlite:
            sql_replacement.update({
                'update_query': ', '.join(['%s=excluded.%s' % (k,k) for k in keys])
            })
        else:
            sql_replacement.update({
                'update_query': ', '.join(['%s=VALUES(%s)' % (k,k) for k in keys])
            })
        query = query % sql_replacement
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
        get_logger().exception("Error in SQL Query for table: %s" % table_name, exc_info=True)
        reraise(e)
    cursor.close()

def _sql_insert_command(on_duplicate_update=True, unique_keys=None):

    if not on_duplicate_update:
        return "INSERT INTO %(table_name)s (%(column_names)s) VALUES %(values_placeholders)s"
    elif unique_keys and len(unique_keys):
        upsert = " ON CONFLICT(%s) DO UPDATE SET %%(update_query)s" % ",".join(["`%s`"%k for k in unique_keys])
        return "INSERT INTO %(table_name)s (%(column_names)s) VALUES %(values_placeholders)s"+upsert
    else:
        return "INSERT INTO %(table_name)s (%(column_names)s) VALUES %(values_placeholders)s ON DUPLICATE KEY UPDATE %(update_query)s"

