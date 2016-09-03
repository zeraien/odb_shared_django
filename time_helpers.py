from datetime import timedelta
import datetime
import re
import calendar
import pytz
from django.conf import settings
from django.utils import timezone

DATETIME_FORMAT = '%Y-%m-%d %H:%M'
FB_DATETIME_FORMAT  = '%Y-%m-%dT%H:%M:%S+0000'

def get_list_of_monday_thru_friday_dates(selected_week_number=None):
    """
        pass a week number and get a list of dates starting on monday of that week.
        if today is a saturday or sunday, return next week instead
    """
    current_week_number, current_weekday = datetime.datetime.now().isocalendar()[1:]
    if selected_week_number is None:
        force = False
        selected_week_number = current_week_number
    else:
        force = True

    page = selected_week_number-current_week_number
    current_monday = (datetime.datetime.now()-datetime.timedelta(days=current_weekday-1)).date()
    selected_monday = current_monday+datetime.timedelta(weeks=page)

    if not force and current_weekday>5 and current_monday==selected_monday:
        selected_monday += datetime.timedelta(days=7)
        selected_week_number+=1
    date_list = [(selected_monday+datetime.timedelta(days=d)) for d in range(0,5)]
    return list(reversed(date_list))


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

    :param dt_object: datetime object
    :return: dictionary
    """
    if dt_object.year == 1970:
        return None
    return {
        "month":dt_object.month,
        "day"  :dt_object.day,
        "year" :dt_object.year
    }
def date_range(start_date, end_date, epoch=True):
    if end_date<start_date:
        days = (start_date-end_date).days
        multiplier = -1
    else:
        multiplier = 1
        days = (end_date-start_date).days

    ranges = []
    for add_days in range(0,days+1):
        ranges.append(
            start_date+timedelta(days=add_days*multiplier)
        )
    return ranges


def get_time_ranges(start_date, end_date, epoch=True):
    """
    Return {'time_start' : DATE, 'time_stop' : DATE}, {'time_start' : DATE+1, 'time_stop' : DATE+1}   ... etc

    :param start_date:
    :param end_date:
    :param epoch: dates become epoch seconds if true, otherwise date objects
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
        @param dt  Datetime object or string
    """
    if dt is None:
        if return_none:
            return None
        else:
            return 0

    if isinstance(dt, datetime.date):
        return int(calendar.timegm(dt.timetuple()))
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
    """Because facebook insists on sending dates and times in a different format in the graph API, we are forced to
    parse this as well"""
    if epo is None:
        return timezone.make_aware(timezone.datetime(1970,1,1), timezone.utc)


    return timezone.make_aware(timezone.datetime.utcfromtimestamp(int(epo)), timezone.utc)

def chunks(l, chunk_size):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), chunk_size):
        yield l[i:i+chunk_size]

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


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

    date ranges are given in an inclusive way, meaning including the first date, and up to and including the last date

    the date ranges are themselves arrays [[start_date, end_date], ....]
    """
    one_day = timedelta(days=1)
    start_date = to_date_object(start_date)
    end_date = to_date_object(end_date)
    corrected_start_date = start_date-one_day
    dates = [corrected_start_date, end_date+one_day] + list(dates)
    dates = sorted(set(dates))

    ranges = []

    dates = dates[dates.index(corrected_start_date):]
    previous_date = dates[0]
    for date in dates[1:]:

        date_diff = date - previous_date

        if date_diff.days > 1:
            current_range = [previous_date+one_day, date-one_day]
            split_ranges = date_range_chunks(current_range[0], current_range[1], chunk_size=max_days_per_range)
            ranges += split_ranges
            # ranges.append(current_range)

        previous_date = date

    return ranges

def to_date_object(date_or_datetime_object):
    if isinstance(date_or_datetime_object, datetime.datetime):
        return date_or_datetime_object.date()
    elif isinstance(date_or_datetime_object, datetime.date):
        return date_or_datetime_object
    else:
        raise TypeError("Object passed is not a date or datetime.")

def get_midnight(dt_obj, add_days = 0):
    tz = pytz.timezone(settings.TIME_ZONE)
    midnight = timezone.datetime(dt_obj.year, dt_obj.month, dt_obj.day)+timedelta(days=add_days)
    return tz.localize(midnight)

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
    date_obj += timedelta(minutes= round_to/2)
    date_obj -= timedelta(minutes=date_obj.minute % round_to,
                             seconds=date_obj.second,
                             microseconds=date_obj.microsecond)
    return date_obj
