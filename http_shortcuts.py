from past.builtins import basestring
import os.path
import simplejson as json

from django.shortcuts import render as django_render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponsePermanentRedirect
from django.utils.decorators import available_attrs

from functools import wraps


def render(request, template, context = {}, ignore_ajax = False, obj=None, content_type=None, status=None, using=None):
    if request.is_ajax() and not ignore_ajax:
        basename = os.path.basename(template)
        if not basename.startswith("_"):
            dirname = os.path.dirname(template)
            template = "%s/_%s"%(dirname,basename)
        response = django_render(request=request, template_name=template, context=context)
    else:
        response = django_render(request,
                                 template_name=template,
                                 context=context,
                                 content_type=content_type,
                                 status=status,
                                 using=using)
    return response
    
def permanent_redirect(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
    def wrapper(request, *args, **kw):
        to = view_func(request, *args, **kw)
        if isinstance(to, basestring):
            return HttpResponsePermanentRedirect(to)
        else:
            return to
    return wrapper
    
def redirect(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
    def wrapper(request, *args, **kw):
        to = view_func(request, *args, **kw)
        if isinstance(to, basestring):
            return HttpResponseRedirect(to)
        else:
            return to
    return wrapper

def render_json(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
    def wrapper(request, *args, **kwargs):
        _json = view_func(request, *args, **kwargs)
        if not isinstance(_json, str) and not isinstance(_json, dict) and not isinstance(_json, list) and not isinstance(_json, tuple):
            return _json
        return HttpResponse(json.dumps(_json), content_type="application/json")
    return wrapper

def render_to(template_name, ignore_ajax=False):
    def renderer(func):
        @wraps(func, assigned=available_attrs(func))
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if not isinstance(output, dict):
                return output
            output['request'] = request
            return render(request, template=template_name, context=output, ignore_ajax=ignore_ajax)
        return wrapper
    return renderer
