from hashid_field.rest import HashidSerializerCharField
from rest_framework import serializers


class ModelSerializerWithGlobalHashidField(serializers.ModelSerializer):
    id = HashidSerializerCharField(read_only=True)
