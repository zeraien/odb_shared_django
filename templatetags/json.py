import json
from django.template import Library
from django.utils.safestring import mark_safe

register = Library()

@register.filter(name='json')
def json_func(obj:dict):
    return mark_safe(json.dumps(obj))
