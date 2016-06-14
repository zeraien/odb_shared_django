import os.path
import json

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, HttpResponsePermanentRedirect
from django.utils.decorators import available_attrs

from functools import wraps


def render(request, template, context = {}, ignore_ajax = False, obj=None, **render_kwargs):
    if request.is_ajax() and not ignore_ajax:
        basename = os.path.basename(template)
        if not basename.startswith("_"):
            dirname = os.path.dirname(template)
            template = "%s/_%s"%(dirname,basename)
        response = render_to_response(template, context)
    else:
        response = render_to_response(template, context, context_instance=RequestContext(request), **render_kwargs)
    return response
    
def permanent_redirect(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
    def wrapper(request, *args, **kw):
        to = view_func(request, *args, **kw)
        if type(to) in (str, unicode):
            return HttpResponsePermanentRedirect(to)
        else:
            return to
    return wrapper
    
def redirect(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
    def wrapper(request, *args, **kw):
        to = view_func(request, *args, **kw)
        if type(to) in (str, unicode):
            return HttpResponseRedirect(to)
        else:
            return to
    return wrapper

def render_json(view_func):
    @wraps(view_func, assigned=available_attrs(view_func))
    def wrapper(request, *args, **kw):
        _json = view_func(request, *args, **kw)
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
