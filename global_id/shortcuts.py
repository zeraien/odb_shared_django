import logging
import re

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.translation import gettext

from .exceptions import DecodeHashidError
from .lib import generate_global_id, decode_global_id

logger = logging.getLogger("ewa.shared")

def update_response_with_global_id(instance, json_data):
    global_id_ = generate_global_id(instance=instance)
    json_data.update({'global_id':global_id_})

def get_object_by_global_id_or_404(queryset, global_id):
    """
    Get from a queryset using either global_id or regular primary key value.

    :param queryset:
    :param global_id: a global id or just an integer ID.
    :return:
    """
    if not hasattr(queryset, 'get'):
        klass__name = queryset.__name__ if isinstance(queryset, type) else queryset.__class__.__name__
        raise ValueError(
            "First argument to get_object_by_global_id_or_404() must be a Manager "
            "or QuerySet, not '%s'." % klass__name
        )
    try:
        if re.match(r"^\d+$", str(global_id)):
            pk = global_id
        else:
            content_type, pk = decode_global_id(global_id)
        try:
            return queryset.get(pk=pk)
        except ObjectDoesNotExist:
            raise Http404(gettext('No %s matches the given query.') % queryset.model._meta.object_name)
    except DecodeHashidError as e:
        logger.debug("Unable to decode the global id [%s] with error [%s]" % (global_id, e))
        raise Http404(gettext('%s is an invalid ID.') % global_id)

def get_object_by_global_id(global_id):
    content_type, pk = decode_global_id(global_id)
    return content_type.get_object_for_this_type(pk=pk)
