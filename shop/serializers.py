import json
from parler_rest.serializers import TranslatableModelSerializer, TranslatedFieldsField
from rest_framework import serializers
from parler.utils.context import switch_language
from .models import *
from django.conf import settings

class SupershopSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Supershop)

    class Meta:
        model = Supershop
        fields = ['id', 'translations', 'image', 'created_at', 'updated_at']

    def to_internal_value(self, data):
        if 'translations' in data and isinstance(data['translations'], str):
            try:
                data['translations'] = json.loads(data['translations'])
            except json.JSONDecodeError:
                raise serializers.ValidationError({'translations': 'Invalid JSON format'})
        return super().to_internal_value(data)

class CategorySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Category)

    class Meta:
        model = Category
        fields = "__all__"

    def to_internal_value(self, data):
        if 'translations' in data and isinstance(data['translations'], str):
            try:
                data['translations'] = json.loads(data['translations'])
            except json.JSONDecodeError:
                raise serializers.ValidationError({'translations': 'Invalid JSON format'})
        return super().to_internal_value(data)

class ProductPriceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPrice
        fields = ['shop', 'price']


class ProductSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Product)
    prices = ProductPriceCreateSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'translations', 'category', 'uom', 'prices']
        
    def create(self, validated_data):
            prices_data = validated_data.pop('prices')
            product = Product.objects.create(**validated_data)
            for price_data in prices_data:
                ProductPrice.objects.create(product=product, **price_data)
            return product