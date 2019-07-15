from django.utils.six import python_2_unicode_compatible
from future import standard_library
standard_library.install_aliases()
import simplejson as json
from django.core import exceptions as django_exceptions
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django import forms
from django_extensions.db.models import TimeStampedModel
from odb_shared import get_logger


class VersionedModel(models.Model):
    class Meta:
        abstract = True
    local_version = models.SmallIntegerField(_('version'), editable=True, default=0)

def versioned_model_pre_save(instance,*args,**kwargs):
    instance.local_version+=1


def simpleTitleComponent(field_name="title"):

    @python_2_unicode_compatible
    class C(models.Model):
        class Meta:
            abstract = True
        def __str__(self):
            return getattr(self, field_name)
    return C

def do_text_markup(markup_language, content):
    if markup_language == "markdown":
        import markdown
        content = markdown.markdown(content)
    elif markup_language == 'textile':
        import textile
        content = textile.textile(content)
    return content

@python_2_unicode_compatible
class NamedTimeStampedModel(TimeStampedModel):
    class Meta:
        abstract = True
    def __str__(self):
        return self.name
    name = models.CharField(_('name'), max_length=255)

class JSONFieldBase(models.Field):
    empty_strings_allowed = False
    prefix = "$json$"
    default_error_messages = {
        'invalid': _("This value must be a valid JSON string."),
    }
    description = _("A JSON Object")

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def get_prep_value(self, value):
        if value is not None and value != '':
            try:
                value = JSONFieldBase.prefix + json.dumps(value)
            except (ValueError, TypeError):
                raise django_exceptions.ValidationError(self.error_messages['invalid'])

        return value

    def from_db_value(self, value, expression, connection):
        return self.to_python(value=value)

    def to_python(self, value):
        is_str = isinstance(value, str)
        if is_str and value.startswith(JSONFieldBase.prefix):
            value = value[len(JSONFieldBase.prefix):]
            try:
                return json.loads(value)
            except (TypeError, ValueError):
                # If an error was raised, just return the plain value
                get_logger().debug('Error processing value [%s] (first 20 chars) of type [%s] for field [%s] (#1)' % (
                value[:20], type(value), self.verbose_name), exc_info=True)
                return value

        return value

    def formfield(self, **kwargs):
        defaults = {'form_class': forms.CharField}
        defaults.update(kwargs)
        return super(JSONFieldBase, self).formfield(**defaults)


class BigJSONField(JSONFieldBase):
    def __init__(self, *args, **kwargs):
        super(BigJSONField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'TextField'

class JSONField(JSONFieldBase):
    def __init__(self, *args, **kwargs):
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 255
        super(JSONField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'CharField'

# http://djangosnippets.org/snippets/513/
import pickle

class PickledObject(str):
    """A subclass of string so it can be told whether a string is
        a pickled object or not (if the object is an instance of this class
        then it must [well, should] be a pickled one)."""
    pass


class PickledObjectField(models.Field):

    def from_db_value(self, value, expression, connection):
        return self.to_python(value=value)

    def to_python(self, value):
        if isinstance(value, PickledObject):
            # If the value is a definite pickle; and an error is raised in de-pickling
            # it should be allowed to propagate.
            return pickle.loads(str(value))
        else:
            try:
                return pickle.loads(str(value))
            except:
                # If an error was raised, just return the plain value
                return value

    def get_db_prep_save(self, value, connection):
        if value is not None and not isinstance(value, PickledObject):
            value = PickledObject(pickle.dumps(value))
        return value

    def get_internal_type(self):
        return 'TextField'

    def get_db_prep_lookup(self, lookup_type, value, connection, prepared=False):
        if lookup_type == 'exact':
            value = self.get_db_prep_save(value)
            return super(PickledObjectField, self).get_db_prep_lookup(lookup_type, value, connection, prepared)
        elif lookup_type == 'in':
            value = [self.get_db_prep_save(v) for v in value]
            return super(PickledObjectField, self).get_db_prep_lookup(lookup_type, value, connection, prepared)
        else:
            raise TypeError('Lookup type %s is not supported.' % lookup_type)

class MoneyField(models.DecimalField):
    description = _("Money")

    def __init__(self, *args, **kwargs):
        kwargs.update(
            default=kwargs.get("default",0),
            max_digits=14,
            decimal_places=2)
        super(MoneyField, self).__init__(*args, **kwargs)

class DefaultModelManager(models.QuerySet):
    def visible(self, **kwargs):
        return self.filter(hidden=False, **kwargs)


class DefaultModel(TimeStampedModel):
    """
    Contains `created_at` and `last_modified_at` fields. Also hidden, and uses a special manager that has a "visible" filter option.
    """
    objects = DefaultModelManager.as_manager()
    hidden = models.BooleanField(_("hidden").capitalize(), default=False)

    class Meta:
        abstract = True
