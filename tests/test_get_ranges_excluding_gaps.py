from ..time_helpers import get_date_ranges_excluding_gaps, \
    daterange, get_month_list
from unittest import TestCase
from datetime import date

class TestGetRangesExcludingGaps(TestCase):
    def test_basic(self):
        dateList = [
            date(2013, 1, 1),
            date(2013, 1, 2),
            date(2013, 1, 3),
            date(2013, 3, 15),
        ]

        expectedResult = [
            [date(2013, 1, 1), date(2013, 1, 4)],
            [date(2013, 3, 15), date(2013, 3, 16)],
        ]

        result = get_date_ranges_excluding_gaps(dates=dateList)
        self.assertListEqual(expectedResult, result)

    def test_split_ranges(self):
        dateList = [
            date(2013, 1, 1),
            date(2013, 1, 2),
            date(2013, 1, 3),
            date(2013, 3, 15),
            date(2013, 3, 16),
            date(2013, 3, 17),
            date(2013, 3, 18),
            date(2013, 3, 19),
            date(2013, 3, 20),
        ]

        expectedResult = [
            [date(2013, 1, 1), date(2013, 1, 3)],
            [date(2013, 1, 3), date(2013, 1, 4)],
            [date(2013, 3, 15), date(2013, 3, 17)],
            [date(2013, 3, 17), date(2013, 3, 19)],
            [date(2013, 3, 19), date(2013, 3, 21)],
        ]

        result = get_date_ranges_excluding_gaps(dates=dateList,
                                                max_days_per_range=2)
        self.assertListEqual(expectedResult, result)

    def test_one_range(self):
        dateList = [
            date(2013, 1, 1),
            date(2013, 1, 2),
            date(2013, 1, 3),
            date(2013, 1, 4),
        ]

        expectedResult = [
            [date(2013, 1, 1), date(2013, 1, 5)],
        ]

        result = get_date_ranges_excluding_gaps(dates=dateList)
        self.assertListEqual(expectedResult, result)

    def test_get_month_list(self):

        d1 = date(2017,7,10)
        d2 = date(2017,10,7)
        l = get_month_list(start_date=d1, end_date=d2)
        expected = [(2017,7),(2017,8),(2017,9),(2017,10)]
        self.assertListEqual(l, expected)
    def test_get_month_list_one_day(self):

        d1 = date(2017,7,9)
        d2 = date(2017,7,10)
        l = get_month_list(start_date=d1, end_date=d2)
        expected = [(2017,7),]
        self.assertListEqual(l, expected)
    def test_get_month_list_zero_days(self):

        d1 = date(2017,7,10)
        d2 = date(2017,7,10)
        l = get_month_list(start_date=d1, end_date=d2)
        expected = [(2017,7),]
        self.assertListEqual(l, expected)

    def test_daterange_positive(self):
        d1 = date(2017,10,10)
        d2 = date(2017,10,7)
        l = list(daterange(start_date=d1, end_date=d2))
        expected = [
            date(2017,10,9),
            date(2017,10,8),
            date(2017,10,7),
        ]
        self.assertListEqual(l, expected)
    def test_daterange_negative(self):
        d1 = date(2017,10,7)
        d2 = date(2017,10,10)
        l = list(daterange(start_date=d1, end_date=d2))
        expected = [
            date(2017,10,7),
            date(2017,10,8),
            date(2017,10,9),
        ]
        self.assertListEqual(l, expected)
