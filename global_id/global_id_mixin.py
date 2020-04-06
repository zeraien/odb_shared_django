from django.db import models

from .lib import generate_global_id


class GlobalIdMixin(models.Model):
    """
    add's a `global_id` method to a Django model class that returns that classes
    global_id.
    A global id is a combination of the ContentType.pk and the model instance pk,
    as well as a version number of the ID format.
    """
    class Meta:
        abstract = True
    def _global_id(self):
        return generate_global_id(self)
    global_id = property(_global_id)

