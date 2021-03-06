from builtins import range
from datetime import timedelta
import datetime

import math
from operator import itemgetter

import re
import calendar
import pytz
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext

DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M'
TIME_FORMAT = '%H:%M'
FB_DATETIME_FORMAT  = '%Y-%m-%dT%H:%M:%S+0000'

def get_list_of_monday_thru_friday_dates(starting_date=None, include_weekend=False):
    """
        pass a week number and get a list of dates starting on monday of that week.
        if today is a saturday or sunday, return next week instead
    """
    current_week_number, current_weekday = datetime.datetime.now().isocalendar()[1:3]
    if starting_date is None:
        force = False
        starting_date = datetime.datetime.now()
    else:
        force = True
    selected_week_number = starting_date.isocalendar()[1]

    current_monday = (datetime.datetime.now()-datetime.timedelta(days=current_weekday-1))
    selected_monday = (starting_date-datetime.timedelta(days=starting_date.isocalendar()[2]-1))

    if not force and current_weekday>5 and to_date_object(current_monday)==to_date_object(selected_monday):
        # if today is already weekend, shift to next week
        # xxx too automagical perhaps...
        selected_monday += datetime.timedelta(days=7)
        selected_week_number+=1
    date_list = [to_date_object(selected_monday+datetime.timedelta(days=d)) for d in range(0,include_weekend and 7 or 5 )]
    return list(date_list)


def range_days(start_date, duration_days, epoch = False):
    time_start = timezone.datetime(start_date.year, start_date.month, start_date.day)
    time_stop = timedelta(hours=24*duration_days)+time_start

    if epoch:
        return {'time_start':to_epoch(time_start), 'time_stop': to_epoch(time_stop)}
    else:
        return {'time_start':time_start, 'time_stop': time_stop}

def total_seconds(time_delta):
    return (time_delta.days * 86400) + time_delta.seconds + (time_delta.microseconds*.000001)

def range_one_day(day = None, epoch = False):
    if day is None:
        day = timezone.now()
    return range_days(day, duration_days=1, epoch=epoch)

def extract_time_range(parameters):
    # time for
    time_start = remote_date_str_to_date(parameters.get('time_start','1970-01-01T00:00:00'))

    time_stop = timezone.now()
    if 'time_stop' in parameters:
        time_stop = remote_date_str_to_date(parameters.get('time_stop'))

    return {'time_start':time_start, 'time_stop':time_stop}

def utc_to_tz(dt_object, timezone):
    localized_dt = pytz.timezone("UTC").localize(dt_object)
    return localized_dt.astimezone(timezone)


def tz_fix_from_account_to_utc(dt_object, timezone):
    if to_epoch(dt_object) > 0:
        localized_dt = timezone.localize(dt_object)
        return localized_dt.astimezone(pytz.timezone("UTC"))
    else:
        return dt_object

def tz_fix_utc_epoch(utc_epoch, timezone):
    """Take a UTC epoch seconds value, and convert it into a date time string in the provided timezone"""
    return timezone.normalize(
                        pytz.utc.localize(
                                    from_epoch(utc_epoch)
                        )
            ).strftime(DATETIME_FORMAT)


def fb_request_timestamp_to_date(dt_object):
    """Convert a datetime object into a facebook stats request date object

    :param datetime.datetime dt_object: datetime object
    :return: dict
    """
    if dt_object.year == 1970:
        return None
    return {
        "month":dt_object.month,
        "day"  :dt_object.day,
        "year" :dt_object.year
    }

def get_month_list(start_date, end_date):
    """
    Return sorted year+month for all dates in the range.

    :param datetime.date start_date:
    :param datetime.date end_date:
    :return: a list of unique year,month tuples for all dates in the range.
    """
    year_months = set()
    if start_date==end_date:
        end_date+=datetime.timedelta(days=1)
    for d in daterange(start_date, end_date):
        year_months.add((d.year, d.month))
    return sorted(list(year_months))

def date_range(start_date, end_date, epoch=True):
    """
    see `daterange`
    """
    return daterange(start_date=start_date, end_date=end_date, epoch=epoch)

def daterange(start_date, end_date, epoch=False, skip_func=None):
    """
    returns a generator that lists all dates starting with `start_date` up to and including `end_date`,
    if `start_date` is newer than `end_date`, the dates are returned in reverse order.

    The date most in the future is never included in the resulting list - the list is end exclusive.

    :param bool epoch: return in unix timestamp at midnight UTC
    :param datetime.date start_date: starting from...
    :param datetime.date end_date: up to and including...
    :param func skip_func: a function that takes a date in the range and returns True or False, if False, do not include the given date.
    :return: generator that iterates dates
    """
    if end_date<start_date:
        days = (start_date-end_date).days
        multiplier = -1
        r = list(range(1,days+1))
    else:
        days = (end_date-start_date).days
        multiplier = 1
        r = list(range(0,days))

    for n in r:
        v = start_date + timedelta(days=n*multiplier)
        skip = False
        if skip_func:
            skip = skip_func(v)

        if not skip:
            if epoch:
                v = to_epoch(get_midnight(v))
            yield v

def get_time_ranges(start_date, end_date, epoch=True):
    """
    Return {'time_start' : DATE, 'time_stop' : DATE}, {'time_start' : DATE+1, 'time_stop' : DATE+1}   ... etc

    :param datetime.date start_date:
    :param datetime.date end_date:
    :param bool epoch: dates become epoch seconds if true, otherwise date objects
    :return:
    """
    if end_date<start_date:
        days = (start_date-end_date).days
        multiplier = -1
    else:
        multiplier = 1
        days = (end_date-start_date).days

    ranges = []
    for add_days in range(0,days+1):
        ranges.append(
            range_days(start_date+timedelta(days=add_days*multiplier), 0, epoch=epoch)
        )
    return ranges

def to_epoch(dt, return_none=False):
    """Return the number of seconds since the epoch in UTC. Accepts strings in an the following datetime format (YYYY-MM-DD HH:MM) or a datetime object.

        :param datetime.datetime dt: Datetime object or string
        :param return_none:  if `dt` is invalid, return None if this is true, otherwise return 0
        :return: the epoch seconds as an `int`
    """
    if dt is None:
        if return_none:
            return None
        else:
            return 0

    if isinstance(dt, datetime.date):
        return int(calendar.timegm(dt.timetuple()))
    elif isinstance(dt, int):
        return dt
    elif not isinstance(dt, datetime.datetime):
        try:
            dt = datetime.datetime.strptime(dt, DATETIME_FORMAT)
        except (TypeError, AttributeError, ValueError):
            return 0

    return int(calendar.timegm(dt.utctimetuple()))

def parse_fb_timestamp(timestamp):
    if re.search(r'^\d\d\d\d\-\d\d\-\d\dT\d\d:\d\d:\d\d\+0000$', timestamp):
        return timezone.datetime.strptime(timestamp, FB_DATETIME_FORMAT)
    else:
        raise ValueError("Invalid facebook timestamp [%s]" % timestamp)

def from_epoch(epo):
    """
    Because facebook insists on sending dates and times in a different format in the graph API, we are forced to
    parse this as well
    :param int epo: epoc seconds to turn into a `datetime.datetime` object
    :type epo: int
    :return: Datetime object
    """
    if epo is None:
        epo = 0
    return pytz.UTC.localize(datetime.datetime.utcfromtimestamp(int(epo)))

def chunks(l, chunk_size):
    """ Yield successive n-sized chunks from l.
    """
    for i in range(0, len(l), chunk_size):
        yield l[i:i+chunk_size]

def get_date_ranges_excluding_gaps(dates, max_days_per_range=30):
    """
    given a list of dates, the dates are returned as a list of ranges, with gaps being excluded and ranges being
    at most `max_days_per_range` long.

    date ranges are given in an exclusive way, meaning including the first date, and UP UNTIL but not including the last date
    TODO: make inclusive
    the date ranges are themselves arrays [[start_date, end_date], ....]
    """

    if len(dates)==0:
        return []

    previous_date = dates[0]
    current_range = [previous_date, previous_date]
    ranges = [current_range]

    for date in dates:

        date_diff = date - previous_date
        range_diff = date - current_range[0]

        if date_diff.days > 1 or range_diff.days >= max_days_per_range:

            current_range = [date, date + datetime.timedelta(days=1)]
            ranges.append(current_range)
        else:
            current_range[1] = date + datetime.timedelta(days=1)

        previous_date = date

    return ranges

def date_range_chunks(start_date, end_date, chunk_size, last_date_excluded=True):
    """
    Given a date range, split it into several chunks being at most
    `chunk_size` days long.

    """
    ranges = []
    date_range_list = list(daterange(start_date, end_date))
    range_list = chunks(date_range_list, chunk_size)
    for current_range in range_list:
        stop_ = current_range[-1]
        if last_date_excluded:
            stop_+=datetime.timedelta(days=1)
        ranges.append([current_range[0], stop_])

    return ranges

def get_gap_ranges_from_dates(dates, start_date, end_date, max_days_per_range=30):
    """
    given a list of dates, the gaps are returned as an array of date ranges.
    The ranges are never longer than `max_days_per_range`.

    date ranges are given in an exclusive way, meaning including the first date, and excluding the last date

    the date ranges are themselves arrays [[start_date, end_date], ....]
    """
    one_day = timedelta(days=1)
    start_date = to_date_object(start_date)
    end_date = to_date_object(end_date)
    corrected_start_date = start_date-one_day
    dates = [corrected_start_date, end_date] + list(dates)
    dates = sorted(set(dates))

    ranges = []

    dates = dates[dates.index(corrected_start_date):]
    previous_date = dates[0]
    for current_date in dates[1:]:

        date_diff = current_date - previous_date

        if date_diff.days > 1:
            current_range = [previous_date+one_day, current_date]
            split_ranges = date_range_chunks(current_range[0],
                                             current_range[1],
                                             chunk_size=max_days_per_range,
                                             last_date_excluded=True)
            ranges += split_ranges

        previous_date = current_date

    return ranges

def to_date_object(date_or_datetime_object):
    if isinstance(date_or_datetime_object, datetime.datetime):
        return date_or_datetime_object.date()
    elif isinstance(date_or_datetime_object, datetime.date):
        return date_or_datetime_object
    else:
        raise TypeError("Object passed is not a date or datetime.")

def get_midnight(dt_obj, add_days = 0):
    tz = timezone.get_current_timezone()
    midnight = timezone.datetime(dt_obj.year, dt_obj.month, dt_obj.day)+timedelta(days=add_days)
    return tz.localize(midnight)

def get_working_hours_in_month(year, month, until_date=None, work_hours_per_day=8):
    hours = 0
    for monthday, weekday in calendar.Calendar(0).itermonthdays2(year=year, month=month):
        if monthday==0 or weekday in (5,6):
            continue
        this_date = datetime.date(year=year, month=month, day=monthday)
        if until_date and this_date>=until_date:
            break
        hours += work_hours_per_day
    return hours

def convert_to_pst(date):
    pst = pytz.timezone("US/Pacific")
    return pst.normalize(date.astimezone(pst))

def midnight_pst(days=0):
    """
    Facebook likes midnights in PST, so we oblige.
    """
    import datetime
    pst = pytz.timezone("US/Pacific")
    pacific_time = convert_to_pst(pytz.utc.localize(datetime.datetime.utcnow()))
    n = pacific_time+timedelta(days=days)
    return pst.localize(datetime.datetime(n.year,n.month,n.day))

def midnight(days=0):
    n = timezone.datetime.utcnow()+timedelta(days=days)
    return timezone.datetime(n.year,n.month,n.day)

def remote_date_str_to_date(strdatetime):
    try:
        return timezone.datetime.strptime(strdatetime, DATETIME_FORMAT)
    except (TypeError, ValueError):
        try:
            return timezone.datetime.strptime(strdatetime, '%Y-%m-%dT%H:%M:%S')
        except (TypeError, ValueError):
            return timezone.datetime(1970,1,1)


def remote_stop_datetime_str_to_time(strdatetime):
    time = remote_datetime_str_to_time(strdatetime)

    if time == datetime.time(hour=0, minute=0):
        time = datetime.time(hour=23, minute=59)
    else:
        time = (timezone.datetime(year=1970, month=1, day=1, hour=time.hour, minute=time.minute) - timedelta(minutes=1)).time()

    return time


def remote_datetime_str_to_time(strdatetime):

    return timezone.datetime.strptime(strdatetime, DATETIME_FORMAT + ':%S').time()


def round_off(date_obj, round_to = 15):
    """
    round the given datetime object to the nearest whole minute.

    :param date_obj: A datetime object.
    :param round_to: Nearest number of minutes to round to. Default is 15.
    :return: The resulting datetime object.
    """
    date_obj += timedelta(minutes=int(round(round_to/2)))
    date_obj -= timedelta(minutes=date_obj.minute % round_to,
                             seconds=date_obj.second,
                             microseconds=date_obj.microsecond)
    return date_obj

def pretty_duration(sec):
    is_negative = sec<0
    sec = math.fabs(sec)

    minutes, seconds = divmod(sec, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    days, hours, minutes, seconds = [int(d) for d in [days, hours, minutes, seconds]]
    return {
        'is_negative':is_negative,
        'days':days,
        'hours':hours,
        'minutes':minutes,
        'seconds':seconds
    }
