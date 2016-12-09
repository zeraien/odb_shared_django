from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.template import Library
from math import ceil, floor

register = Library()

@register.filter
def time_from_minutes(total_minutes):
    return time_from_seconds(total_minutes*60.)
time_from_minutes.is_safe=True

@register.filter
def time_from_seconds(total_seconds):
    if total_seconds is None or type(total_seconds) not in (int, long, float):
        return ""

    hours, remainder = divmod(total_seconds, 3600)
    hours = int(hours)
    minutes = int(floor(remainder // 60))
    seconds = int(round(remainder - (minutes * 60)))

    timedata = {
        'hours':hours,
        'minutes':minutes,
        'seconds':seconds
    }

    if minutes == 0:
        return mark_safe(_("%(seconds)ss") % timedata)
    elif hours == 0:
        return mark_safe(_("%(minutes)sm %(seconds)ss") % timedata)
    elif seconds == 0:
        return mark_safe(_("%(hours)sh %(minutes)sm") % timedata)
    else:
        return mark_safe(_("%(hours)sh %(minutes)sm %(seconds)ss") % timedata)

time_from_seconds.is_safe=True
