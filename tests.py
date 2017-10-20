from time_helpers import get_gap_ranges_from_dates, date_range_chunks, get_time_ranges, get_date_ranges_excluding_gaps, \
    daterange, get_month_list
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

    def test_get_working_hours_in_month(self):
        from odb_shared.time_helpers import get_working_hours_in_month
        test_year, test_month = 2017, 10
        hours = get_working_hours_in_month(year=test_year, month=test_month, work_hours_per_day=1)
        self.assertEqual(22, hours)

        test_year, test_month = 2017, 12
        hours = get_working_hours_in_month(year=test_year, month=test_month, work_hours_per_day=2)
        self.assertEqual(42, hours)

    def test_get_date_ranges(self):
        dateStart = date(2013, 7, 5)
        dateEnd = date(2013, 7, 8)
        ranges = get_time_ranges(start_date=dateStart,end_date=dateEnd,epoch=False)
        expected_result = [
            {'time_start': datetime(2013, 7, 5, 0, 0), 'time_stop': datetime(2013, 7, 5, 0, 0)},
            {'time_start': datetime(2013, 7, 6, 0, 0), 'time_stop': datetime(2013, 7, 6, 0, 0)},
            {'time_start': datetime(2013, 7, 7, 0, 0), 'time_stop': datetime(2013, 7, 7, 0, 0)},
            {'time_start': datetime(2013, 7, 8, 0, 0), 'time_stop': datetime(2013, 7, 8, 0, 0)},
        ]
        self.assertListEqual(ranges, expected_result)


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
            [date(2013, 7, 5), date(2013, 7, 10)],
            [date(2013, 7, 10), date(2013, 7, 15)],
            [date(2013, 7, 15), date(2013, 7, 20)],
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
            [date(2013, 7, 5), date(2013, 7, 10)],
            [date(2013, 7, 10), date(2013, 7, 15)],
            [date(2013, 7, 15), date(2013, 7, 20)],
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
            [date(2012, 12, 15), date(2013, 1, 1)],
            [date(2013,  1, 4), date(2013,  1, 7)],
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

        expectedResult = [[date(2013, 1, 4), date(2013, 1, 8)]]

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
            [date(2013, 1, 4), date(2013, 1, 7)],
            [date(2013, 1, 9), date(2013, 1, 10)],
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
            [date(2013, 1, 4),date(2013, 1, 6)],
            [date(2013, 1, 6),date(2013, 1, 8)],
            [date(2013, 1, 8),date(2013, 1, 10)],
            [date(2013, 1, 13),date(2013, 1, 15)],
            [date(2013, 1, 15),date(2013, 1, 17)],
            [date(2013, 1, 17),date(2013, 1, 19)],
        ]

        gapResult = get_gap_ranges_from_dates(dateList,
                                              start_date=dateList[0],
                                              end_date=dateList[-1],
                                              max_days_per_range=2)

        self.assertListEqual(expectedResult, gapResult)

    def test_date_range_chunks(self):
        start_date = date(2013, 1, 2)
        end_date = date(2013, 1, 10)
        chunk_size = 3
        last_date_excluded = True
        chunks = date_range_chunks(start_date,
                          end_date,
                          chunk_size,
                          last_date_excluded=last_date_excluded)
        expected_result = [
            [date(2013, 1, 2), date(2013, 1, 5)],
            [date(2013, 1, 5), date(2013, 1, 8)],
            [date(2013, 1, 8), date(2013, 1, 10)],
        ]
        self.assertListEqual(chunks, expected_result)

    def test_date_list_gap_max_range_30_days(self):

        dateList = [
            date(2013, 1, 1),
            date(2013, 1, 2),
            date(2013, 1, 3),
            date(2013, 3, 15),
        ]

        expectedResult = [
            [date(2013, 1, 4), date(2013, 2, 3)],
            [date(2013, 2, 3), date(2013, 3, 5)],
            [date(2013, 3, 5), date(2013, 3, 15)],
        ]

        gapResult = get_gap_ranges_from_dates(dateList, start_date=dateList[0], end_date=dateList[-1], max_days_per_range=30)

        self.assertListEqual(expectedResult, gapResult)

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
