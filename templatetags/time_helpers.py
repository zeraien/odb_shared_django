from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.template import Library
from math import ceil, floor

from odb_shared.time_helpers import pretty_duration, to_epoch, from_epoch

register = Library()

@register.filter
def time_from_minutes(total_minutes):
    if total_minutes is None or type(total_minutes) not in (int, long, float):
        total_minutes = 0
    return time_from_seconds(total_minutes*60.)
time_from_minutes.is_safe=True

@register.filter
def time_from_seconds(total_seconds, show_seconds=False):
    if total_seconds is None or type(total_seconds) not in (int, long, float):
        return ""
    timedata = pretty_duration(total_seconds)

    days = timedata['days']
    hours = timedata['hours']
    minutes = timedata['minutes']
    seconds = timedata['seconds']

    if not show_seconds:
        if days > 0:
            if hours==0 and minutes==0:
                return mark_safe(_("%(days)sd") % timedata)
            elif minutes==0:
                return mark_safe(_("%(days)sd %(hours)sh") % timedata)
            else:
                return mark_safe(_("%(days)sd %(hours)sh %(minutes)smin") % timedata)
        elif hours>0:
            if minutes==0:
                return mark_safe(_("%(hours)sh") % timedata)
            else:
                return mark_safe(_("%(hours)sh %(minutes)smin") % timedata)
        elif minutes>1:
            return mark_safe(_("%(minutes)smin") % timedata)
        elif seconds>0:
            return mark_safe(_("%(seconds)ss") % timedata)
        else:
            return mark_safe("0")
    else:
        if days > 0:
            return mark_safe(_("%(days)sd %(hours)sh %(minutes)smin %(seconds)ss") % timedata)
        elif hours>0:
            return mark_safe(_("%(hours)sh %(minutes)smin %(seconds)ss") % timedata)
        elif minutes>1:
            return mark_safe(_("%(minutes)smin %(seconds)ss") % timedata)
        elif seconds>0:
            return mark_safe(_("%(seconds)ss") % timedata)
        else:
            return mark_safe("0")

time_from_seconds.is_safe=True


@register.filter(name="from_epoch")
def from_epoch_filter(dt):
    return from_epoch(dt)

@register.filter(name="to_epoch")
def to_epoch_filter(dt):
    return to_epoch(dt)
