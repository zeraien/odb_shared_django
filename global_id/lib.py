import logging
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from hashid_field import Hashid

from . import DecodeHashidError
from .hashids_lib import generate_identifier, decode_identifier

GLOBAL_ID_VERSION = 1
logger = logging.getLogger("ewa.shared")

#todo cache this value
def generate_global_id(instance, generator=None):
    """
    Get the global ID for any django model instance.

    A global id is a combination of the ContentType.pk and the model instance pk,
    as well as a version number of the ID format.

    :param instance: A django model instance
    :param generator: a custom Hashids instance
    :return: The global id
    """
    pk = isinstance(instance.pk,Hashid) and instance.pk.id or instance.pk
    ct = ContentType.objects.get_for_model(instance)

    return generate_identifier(
        generator=generator,
        version=GLOBAL_ID_VERSION,
        content_type=ct.pk,
        pk=pk
    )

def generate_global_id_for_model_name_and_pk(model_name, pk, generator=None):
    app_label, model_class_name = model_name.rsplit('.',1)
    try:
        model = apps.get_model(app_label=app_label, model_name=model_class_name)
        ct = ContentType.objects.get_for_model(model)
    except ContentType.DoesNotExist:
        raise DecodeHashidError("Unable to find ContentType `%s`"%model_name)

    return generate_identifier(
        generator=generator,
        version=GLOBAL_ID_VERSION,
        content_type=ct.pk,
        pk=pk
    )

def decode_global_id_list(l, generator=None):
    """
    A list of global-id encoded hashids.

    A global id is a combination of the ContentType.pk and the model instance pk,
    as well as a version number of the ID format.

    :param l: a list of hashid-type global IDs.
    :param generator:  A custom Hashids instance if you're too fancy for the default
    :return:
    """
    return [
        decode_identifier(
            generator=generator,
            version=GLOBAL_ID_VERSION,
            identifier=i,
            keys=['pk','content_type']
        )['pk'] for i in l
    ]

def decode_global_id(global_id, no_lookup=False, generator=None):
    """
    A global id is a combination of the ContentType.pk and the model instance pk,
    as well as a version number of the ID format.

    :param generator:  A custom Hashids instance if you're too fancy for the default
    :param no_lookup: If True, just return the content_type_id, otherwise return the content type object itself.
    :param global_id:
    :return: returns content_type, pk
    """
    data = decode_identifier(
        generator=generator,
        version=GLOBAL_ID_VERSION,
        identifier=global_id,
        keys=['pk','content_type']
    )
    if no_lookup:
        return data['content_type'], data['pk']
    else:
        content_type = ContentType.objects.get_for_id(data['content_type'])
        return content_type, data['pk']

