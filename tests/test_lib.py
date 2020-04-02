# coding=utf-8
import hashlib
from unittest import TestCase

from ..lib import make_query_string_from_data


class TestMakeQueryString(TestCase):
    def test_make_query_string_from_unicode_data(self):
        q = make_query_string_from_data(foo=u"barä", baz="bazinga")
        self.assertEqual(q,"baz=bazinga&foo=barä")

        q = make_query_string_from_data(foo=[u"barä","far"], baz="bazinga")
        self.assertEqual(q,"baz=bazinga&foo=[barä,far]")

    def test_make_query_string_with_ints(self):
        q = make_query_string_from_data(**{'test':[4,"ÄFOO","BAR"]})
        self.assertEqual(q,"test=[4,ÄFOO,BAR]")

    def test_make_query_string_from_data(self):
        # regular test
        q = make_query_string_from_data(foo="bar")
        self.assertEqual(q,"foo=bar")
        # two keys
        q = make_query_string_from_data(foo="bar", baz="bazinga")
        self.assertEqual(q,"baz=bazinga&foo=bar")

        # too long
        maxlen = 100
        q = make_query_string_from_data(
            _max_length=maxlen,
            foo="bar baz brah bilar bilar",
            baz="lorem ipsum dolor metis poop",
            oswald="brah brass bruh bri brack",
            poop="pipipi piri piri sauce")
        h = hashlib.sha1("baz=lorem ipsum dolor metis poop&foo=bar baz brah bilar bilar&oswald=brah brass bruh bri brack&poop=pipipi piri piri sauce".encode("utf8")).hexdigest()
        self.assertEqual("baz=lorem ipsum dolor metis poop&foo=bar baz brah bilar bil-%s"%h,q)
        self.assertEqual(maxlen, len(q))
