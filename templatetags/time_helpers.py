from django.utils.translation import ugettext as _
from django.template import Library
from math import ceil, floor

register = Library()

@register.filter
def time_from_seconds(total_seconds):
    if total_seconds is None or type(total_seconds) not in (int, long):
        return ""

    hours, remainder = divmod(total_seconds, 3600)
    minutes = int(floor(remainder // 60))
    seconds = int(round(remainder - (minutes * 60)))

    timedata = {
        'hours':hours,
        'minutes':minutes,
        'seconds':seconds
    }

    if minutes == 0:
        return _("%(seconds)ss") % timedata
    elif hours == 0:
        return _("%(minutes)sm %(seconds)ss") % timedata
    else:
        return _("%(hours)sh %(minutes)sm %(seconds)ss") % timedata
