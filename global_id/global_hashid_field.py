from functools import total_ordering

from hashid_field import Hashid
from hashid_field.descriptor import HashidDescriptor
from hashid_field.field import HashidAutoField

from .hashids_lib import get_hashids
from .lib import decode_global_id, generate_global_id_for_model_name_and_pk
from .exceptions import DecodeHashidError


class GlobalHashid(Hashid):
    def __init__(self, model_name, *args, **kwargs):
        self._model_name = model_name
        super(GlobalHashid, self).__init__(*args, **kwargs)

    def encode(self, id):
        return generate_global_id_for_model_name_and_pk(
            model_name=self._model_name,
            pk=id,
            generator=self.hashids
        )

    def decode(self, hashid):
        try:
            content_type_id, pk = decode_global_id(hashid,
                                    no_lookup=True,
                                    generator=self.hashids)
        except DecodeHashidError:
            return None
        if pk:
            return pk
        else:
            return None

    def __repr__(self):
        return "GlobalHashid({}): {}".format(self._id, self._hashid)

    def __reduce__(self):
        return (self.__class__, (self._model_name, self._id, self._salt, self._min_length, self._alphabet))

_ALREADY_REGISTERED = []

class GlobalHashidDescriptor(HashidDescriptor):
    def __init__(self, model_name, *args, **kwargs):
        self.model_name = model_name
        super(GlobalHashidDescriptor, self).__init__(*args, **kwargs)

    def __set__(self, instance, value):
        if isinstance(value, Hashid) or value is None:
            instance.__dict__[self.name] = value
        else:
            try:
                instance.__dict__[self.name] = GlobalHashid(model_name=self.model_name, id=value, salt=self.salt, min_length=self.min_length, alphabet=self.alphabet)
            except ValueError:
                instance.__dict__[self.name] = value


class PlaceholderHashidAutoField(HashidAutoField):
    pass

def GlobalHashidAutoFieldFactory(model_name):
    assert model_name not in _ALREADY_REGISTERED, "Failed to register `%s` with hashidAutoPk, because it's already registered"%model_name

    class GlobalHashidAutoField(HashidAutoField):
        def contribute_to_class(self, cls, name, **kwargs):
            super().contribute_to_class(cls, name, **kwargs)
            setattr(
                cls,
                self.attname,
                GlobalHashidDescriptor(
                    model_name=model_name,
                    name=self.attname,
                    salt=self.salt,
                    min_length=self.min_length,
                    alphabet=self.alphabet
                )
            )

        def encode_id(self, id):
            return GlobalHashid(id=id,
                                model_name=model_name,
                                salt=self.salt,
                                min_length=self.min_length,
                                alphabet=self.alphabet)

    _ALREADY_REGISTERED.append(model_name)

    model_class_name = model_name.rsplit('.',1)[-1]
    newclass = type(
        'PlaceholderHashidAutoField',
        # '%sGlobalHashidAutoField' % model_class_name,
        (GlobalHashidAutoField,),
        {}
    )
    return newclass
