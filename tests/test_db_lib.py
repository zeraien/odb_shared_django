from unittest import TestCase

from odb_shared.db_lib import get_query_for_data_pairs


class Test(TestCase):

    def test_get_query_for_data_pairs(self):

        with self.assertRaises(ValueError):
            data_pairs = ["foo", "bar"]
            get_query_for_data_pairs(data_pairs, "id_foo", "table_bar", limit_to_ids=[])

        data_pairs = [("key", "ängsbacken")]
        get_query_for_data_pairs(data_pairs, "id_foo", "table_bar", limit_to_ids=[])

        data_pairs = [(1, 'bar')]
        get_query_for_data_pairs(data_pairs, "id_foo", "table_bar", limit_to_ids=[])

        data_pairs = [("key", 1)]
        get_query_for_data_pairs(data_pairs, "id_foo", "table_bar", limit_to_ids=[])

    def test_case_1(self):
        data_pairs = [
            ("keyaz","valueaz")
        ]
        q,values = get_query_for_data_pairs(data_pairs, "id_foo", "table_bar", limit_to_ids=[])
        self.assertEqual(
            'SELECT D0.id_foo as `id` FROM table_bar as D0 WHERE (D0.key=%(key0)s AND D0.value IN (%(val0.0)s)) GROUP BY D0.id_foo ORDER BY D0.id_foo',
            q
        )
        self.assertDictEqual(values, {'key0': "keyaz", 'val0.0': "valueaz"})

    def test_case_2(self):
        data_pairs = [
            ("key",["value1","value2"])
        ]
        q,values = get_query_for_data_pairs(data_pairs, "id_foo", "table_bar", limit_to_ids=[])
        self.assertEqual(
            'SELECT D0.id_foo as `id` FROM table_bar as D0 WHERE (D0.key=%(key0)s AND D0.value IN (%(val0.0)s,%(val0.1)s)) GROUP BY D0.id_foo ORDER BY D0.id_foo',
            q
        )
        self.assertDictEqual(values, {'key0': "key", 'val0.0': "value1", 'val0.1': "value2"})

    def test_case_3(self):
        data_pairs = [
            ("key1foobarvalue",["the_value1","the_value2"]),
            ("key2bzainga",["the_value2.1","the_value2.2"])
        ]
        q,values = get_query_for_data_pairs(data_pairs, "id_foo", "table_bar", limit_to_ids=[])
        self.assertEqual(
            'SELECT D0.id_foo as `id` FROM table_bar as D0  LEFT JOIN table_bar as D1 ON D0.id_foo = D1.id_foo WHERE (D0.key=%(key0)s AND D0.value IN (%(val0.0)s,%(val0.1)s)) AND (D1.key=%(key1)s AND D1.value IN (%(val1.0)s,%(val1.1)s)) GROUP BY D0.id_foo ORDER BY D0.id_foo',
            q
        )
        self.assertDictEqual(values, {'key0': "key1foobarvalue",
                                      'key1':'key2bzainga',
                                      'val0.0': "the_value1",
                                      'val0.1': "the_value2",
                                      'val1.0': "the_value2.1",
                                      'val1.1': "the_value2.2"})

    def test_with_limit_to_ids(self):
        data_pairs = [
            ("k","v")
        ]
        q,values = get_query_for_data_pairs(data_pairs, "id_foo", "table_bar", limit_to_ids=[1,2,3])
        self.assertEqual(
            'SELECT D0.id_foo as `id` FROM table_bar as D0 WHERE D0.id_foo IN (%(id0)s,%(id1)s,%(id2)s) AND (D0.key=%(key0)s AND D0.value IN (%(val0.0)s)) GROUP BY D0.id_foo ORDER BY D0.id_foo',
            q
        )
        self.assertDictEqual(values, {
            'id0': 1, 'id1': 2, 'id2': 3,
            'key0': "k",'val0.0': "v",})
