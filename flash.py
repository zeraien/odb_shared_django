#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.utils.encoding import smart_unicode

class Flash:
    def __init__(self, message, is_error=False):
        self.message = message.encode('utf8')
        self.is_error = is_error

    def __repr__(self):
        return self.message

    def __str__(self):
        return self.message


def exists(request):
    return 'flash_data' in request.session


def clear(request):
    if exists(request):
        del(request.session['flash_data'])


class FlashWrapper(object):
    def __init__(self, request):
        self.request = request

    def __len__(self):
        return len(self.request.session.get('flash_data', []))

    def __nonzero__(self):
        return len(self) > 0

    def has_only_errors(self):
        msgs = self.get()
        for msg in msgs:
            if not msg.is_error:
                return False
        return True

    def get(self):
        flash_ = None
        if exists(self.request):
            flash_ = self.request.session['flash_data']
        else: flash_ = []
        return flash_

    def get_and_clear(self):
        flash_ = None
        if exists(self.request) and self.request.session.has_key('flash_data'):
            flash_ = self.request.session['flash_data']
            clear(self.request)
        else: flash_ = []
        return flash_


def get(request):
    return FlashWrapper(request)


def append(request, message):
    if not exists(request):
        request.session['flash_data'] = []

    request.session['flash_data'].append(Flash(message))
    request.session.save()


def error(request, message):
    clear(request)
    append_error(request, message)


def append_error(request, message):
    if not exists(request):
        request.session['flash_data'] = []

    request.session['flash_data'].append(Flash(message, True))
    request.session.save()


def set(request, message):
    clear(request)
    append(request, message)
