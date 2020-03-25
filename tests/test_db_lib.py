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

        data_pairs = [
            ("key","value")
        ]
        q = get_query_for_data_pairs(data_pairs, "id_foo", "table_bar", limit_to_ids=[])
        self.assertEqual(
            'SELECT D0.id_foo as `id` FROM table_bar as D0 WHERE (D0.key="key" AND D0.value IN ("value")) GROUP BY D0.id_foo ORDER BY D0.id_foo',
            q
        )

        data_pairs = [
            ("key",["value1","value2"])
        ]
        q = get_query_for_data_pairs(data_pairs, "id_foo", "table_bar", limit_to_ids=[])
        self.assertEqual(
            'SELECT D0.id_foo as `id` FROM table_bar as D0 WHERE (D0.key="key" AND D0.value IN ("value1","value2")) GROUP BY D0.id_foo ORDER BY D0.id_foo',
            q
        )

        data_pairs = [
            ("key1",["value1","value2"]),
            ("key2",["value2.1","value2.2"])
        ]
        q = get_query_for_data_pairs(data_pairs, "id_foo", "table_bar", limit_to_ids=[])
        self.assertEqual(
            'SELECT D0.id_foo as `id` FROM table_bar as D0  LEFT JOIN table_bar as D1 ON D0.id_foo = D1.id_foo WHERE (D0.key="key1" AND D0.value IN ("value1","value2")) AND (D1.key="key2" AND D1.value IN ("value2.1","value2.2")) GROUP BY D0.id_foo ORDER BY D0.id_foo',
            q
        )
