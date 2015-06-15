from time_helpers import get_gap_ranges_from_dates
from django.test import TestCase
from datetime import date, timedelta, datetime

__author__ = 'zeraien'


class ODBSharedTest(TestCase):

    def test_error_case1(self):

        dateStart = datetime(2013, 7, 6)
        dateEnd = datetime(2013, 7, 10)

        dateList = [
            date(2013, 7, 5),
            date(2013, 7, 6),
            date(2013, 7, 7),
        ]

        expectedGaps = [
            [date(2013, 7, 8), date(2013, 7, 10)],
        ]

        gapResult = get_gap_ranges_from_dates(dateList, start_date=dateStart, end_date=dateEnd, max_days_per_range=5)

        self.assertListEqual(expectedGaps, gapResult)

    def test_with_no_dates_at_all(self):
        dateStart = date(2013, 7, 5)
        dateEnd = date(2013, 7, 20)

        dateList = [
        ]

        expectedGaps = [
            [date(2013, 7, 5), date(2013, 7, 20)],
        ]

        gapResult = get_gap_ranges_from_dates(dateList, start_date=dateStart, end_date=dateEnd)

        self.assertListEqual(expectedGaps, gapResult)


    def test_if_since_is_after_earliest_date_in_list2(self):

        dateStart = date(2013, 7, 5)
        dateEnd = date(2013, 7, 20)

        dateList = [
            date(2013, 7, 1),
        ]

        expectedGaps = [
            [date(2013, 7, 5), date(2013, 7, 9)],
            [date(2013, 7, 10), date(2013, 7, 14)],
            [date(2013, 7, 15), date(2013, 7, 19)],
            [date(2013, 7, 20), date(2013, 7, 20)],
        ]

        gapResult = get_gap_ranges_from_dates(dateList, start_date=dateStart, end_date=dateEnd, max_days_per_range=5)

        self.assertListEqual(expectedGaps, gapResult)

    def test_if_since_is_after_earliest_date_in_list(self):

        dateStart = date(2013, 7, 5)
        dateEnd = date(2013, 7, 20)

        dateList = [
            date(2013, 7, 1),
            date(2013, 7, 2),
            date(2013, 7, 3),
        ]

        expectedGaps = [
            [date(2013, 7, 5), date(2013, 7, 9)],
            [date(2013, 7, 10), date(2013, 7, 14)],
            [date(2013, 7, 15), date(2013, 7, 19)],
            [date(2013, 7, 20), date(2013, 7, 20)],
        ]

        gapResult = get_gap_ranges_from_dates(dateList, start_date=dateStart, end_date=dateEnd, max_days_per_range=5)

        self.assertListEqual(expectedGaps, gapResult)


    def test_date_list_gap_with_start_end(self):

        dateStart = date(2012, 12, 15)
        dateEnd = date(2013, 2, 1)

        dateList = [
            date(2013, 1, 1),
            date(2013, 1, 2),
            date(2013, 1, 3),
            date(2013, 1, 7),
            date(2013, 1, 8),
        ]

        expectedGaps = [
            [date(2012, 12, 15), date(2012, 12, 31)],
            [date(2013,  1, 4), date(2013,  1, 6)],
            [date(2013,  1, 9), date(2013,  2, 1)],
        ]

        gapResult = get_gap_ranges_from_dates(dateList, start_date=dateStart, end_date=dateEnd)

        self.assertListEqual(expectedGaps, gapResult)


    def test_date_list_gap(self):

        dateList = [
            date(2013, 1, 1),
            date(2013, 1, 2),
            date(2013, 1, 3),
            date(2013, 1, 8),
            date(2013, 1, 9),
        ]

        expectedResult = [[date(2013, 1, 4), date(2013, 1, 7)]]

        gapResult = get_gap_ranges_from_dates(dateList, start_date=dateList[0], end_date=dateList[-1])

        self.assertListEqual(expectedResult, gapResult)

    def test_date_list_gaps(self):

        dateList = [
            date(2013, 1, 1),
            date(2013, 1, 2),
            date(2013, 1, 3),
            date(2013, 1, 7),
            date(2013, 1, 8),
            date(2013, 1, 10),
            date(2013, 1, 11)
        ]

        expectedResult = [
            [date(2013, 1, 4), date(2013, 1, 6)],
            [date(2013, 1, 9), date(2013, 1, 9)],
        ]

        gapResult = get_gap_ranges_from_dates(dateList, start_date=dateList[0], end_date=dateList[-1])

        self.assertListEqual(expectedResult, gapResult)

    def test_date_list_gap_max_range_2_days(self):

        dateList = [
            date(2013, 1, 3),
            date(2013, 1, 10),
            date(2013, 1, 11),
            date(2013, 1, 12),
            date(2013, 1, 19)
        ]

        expectedResult = [
            [date(2013, 1, 4),date(2013, 1, 5)],
            [date(2013, 1, 6),date(2013, 1, 7)],
            [date(2013, 1, 8),date(2013, 1, 9)],
            [date(2013, 1, 13),date(2013, 1, 14)],
            [date(2013, 1, 15),date(2013, 1, 16)],
            [date(2013, 1, 17),date(2013, 1, 18)],
        ]

        gapResult = get_gap_ranges_from_dates(dateList, start_date=dateList[0], end_date=dateList[-1], max_days_per_range=2)

        self.assertListEqual(expectedResult, gapResult)

    def test_date_list_gap_max_range_30_days(self):

        dateList = [
            date(2013, 1, 1),
            date(2013, 1, 2),
            date(2013, 1, 3),
            date(2013, 3, 15),
        ]

        expectedResult = [
            [date(2013, 1, 4), date(2013, 2, 2)],
            [date(2013, 2, 3), date(2013, 3, 4)],
            [date(2013, 3, 5), date(2013, 3, 14)],
        ]

        gapResult = get_gap_ranges_from_dates(dateList, start_date=dateList[0], end_date=dateList[-1], max_days_per_range=30)

        self.assertListEqual(expectedResult, gapResult)
