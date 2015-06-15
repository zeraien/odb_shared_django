from django import template
from django.forms import widgets
register = template.Library()

@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, widgets.CheckboxInput)
@register.filter
def is_checkbox_multiple(field):
    return isinstance(field.field.widget, widgets.CheckboxSelectMultiple)
