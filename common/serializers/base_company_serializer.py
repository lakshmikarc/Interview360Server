from rest_framework import serializers
from companies.models import Company
from profiles.fields import AttachmentField
from .base_attachment_serializer import BaseAttachmentSerializer


class BaseCompanySerializer(serializers.ModelSerializer):
    """Base Company Serializer class."""

    attachment = serializers.SerializerMethodField()

    class Meta:
        """Metaclass for serializer."""

        model = Company
        fields = [
            'id',
            'name',
            'city',
            'country',
            'description',
            'start_date',
            'created_at',
            'attachment'
        ]

    def get_attachment(self, obj):
        """Get attachment object."""

        last_attachment = obj.images.last()
        if last_attachment:
            return BaseAttachmentSerializer(last_attachment).data
        else:
            return None
