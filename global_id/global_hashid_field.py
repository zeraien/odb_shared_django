from hashid_field import Hashid
from hashid_field.field import HashidAutoField
from .lib import decode_global_id, generate_global_id_for_model_name_and_pk
from .exceptions import DecodeHashidError


class GlobalHashid(Hashid):
    def __init__(self,model_name, *args, **kwargs):
        self._model_name = model_name
        super(GlobalHashid, self).__init__(*args, **kwargs)

    def encode(self, id):
        return generate_global_id_for_model_name_and_pk(
            model_name=self._model_name,
            pk=id,
            generator=self._hashids
        )

    def decode(self, hashid):
        try:
            content_type_id, pk = decode_global_id(hashid,
                                    no_lookup=True,
                                    generator=self._hashids)
        except DecodeHashidError:
            return None
        if pk:
            return pk
        else:
            return None

    def __reduce__(self):
        return (self.__class__, (self._model_name, self._id, self._salt, self._min_length, self._alphabet))

class GlobalHashidAutoField(HashidAutoField):
    def encode_id(self, id):
        return GlobalHashid(id=id,
                            model_name=self.get_model_name(),
                            salt=self.salt,
                            min_length=self.min_length,
                            alphabet=self.alphabet)
_ALREADY_REGISTERED = []

def GlobalHashidAutoFieldFactory(model_name):
    assert model_name not in _ALREADY_REGISTERED, "Failed to register `%s` with hashidAutoPk, because it's already registered"%model_name

    def get_model_name(self):
        return model_name

    _ALREADY_REGISTERED.append(model_name)

    model_class_name = model_name.rsplit('.',1)[-1]
    newclass = type('%sGlobalHashidAutoField' % model_class_name, (GlobalHashidAutoField,), {"get_model_name": get_model_name})
    return newclass
