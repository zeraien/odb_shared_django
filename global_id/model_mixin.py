from .global_hashid_field import GlobalHashidAutoFieldFactory
from django.db import models

def GlobalHashidModelFactory(model_name):
    """
    Pass a model name as you would in django, with `app_label.model_name`.
    This will add a primary key auto field that is an int, but appears
    as a Hashids string everywhere else, using my global-id generation
    schema.

    :param model_name: `app_label.model_name`
    :return: A class to add as a mixin to any django model
    """
    class GlobalHashidModel(models.Model):
        class Meta:
            abstract = True
        id = GlobalHashidAutoFieldFactory(model_name)(primary_key=True)

    return GlobalHashidModel
