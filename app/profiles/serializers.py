from rest_framework import serializers
from attachments.models import Image
from drf_writable_nested import WritableNestedModelSerializer
from common.serializers.user_serializer import UserSerializer
from .fields import AttachmentField
from .index import UserIndex
import ipdb


class ProfileSerializer(serializers.ModelSerializer):
    """User profile serializer."""

    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=255, required=True)
    last_name = serializers.CharField(max_length=255, required=True)
    attachment = AttachmentField(required=False, allow_null=True)

    class Meta:
        """Serializer's metaclass."""

        model = UserSerializer.Meta.model
        fields = UserSerializer.Meta.fields

    def update(self, instance, data):
        """Update existent profile."""

        instance.email = data.get('email', instance.email)
        instance.first_name = data.get('first_name', instance.first_name)
        instance.last_name = data.get('last_name', instance.last_name)
        attachment_json = data.get('attachment')

        if attachment_json:
            attachment_id = attachment_json.get('id')
            attachment = Image.objects.get(id=attachment_id)
            attachment.object_id = instance.id
            attachment.save()

        instance.save()
        UserIndex.store_index(instance)
        return instance
