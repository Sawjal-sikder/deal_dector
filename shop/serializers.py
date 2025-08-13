import json
from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField
from rest_framework import serializers
from .models import Supershop

class SupershopSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Supershop)

    class Meta:
        model = Supershop
        fields = ['id', 'translations', 'image', 'created_at', 'updated_at']

    def to_internal_value(self, data):
        # Convert stringified JSON to dict
        if 'translations' in data and isinstance(data['translations'], str):
            try:
                data['translations'] = json.loads(data['translations'])
            except json.JSONDecodeError:
                raise serializers.ValidationError({'translations': 'Invalid JSON format'})
        return super().to_internal_value(data)
