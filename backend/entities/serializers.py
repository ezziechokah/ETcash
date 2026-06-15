from rest_framework import serializers

from .models import LegalEntity


class LegalEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = LegalEntity
        fields = ['id', 'code', 'name', 'kra_pin', 'currency', 'is_default', 'created_at']
