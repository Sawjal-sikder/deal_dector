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

class ProductImageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']
        extra_kwargs = {
            'image': {'required': True, 'allow_null': False}
        }

class ProductPriceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPrice
        fields = ['shop', 'price']

class ProductListSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Product)
    prices = ProductPriceCreateSerializer(many=True, read_only=True)
    images = ProductImageCreateSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'category', 'translations', 'prices', 'images']

class ProductCreateSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Product)
    prices = ProductPriceCreateSerializer(many=True, required=False)
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True
    )

    class Meta:
        model = Product
        fields = ['category', 'translations', 'prices', 'images']

    def to_internal_value(self, data):
        """Parse JSON strings before validation."""
        if 'translations' in data and isinstance(data['translations'], str):
            try:
                data['translations'] = json.loads(data['translations'])
            except json.JSONDecodeError:
                raise serializers.ValidationError({'translations': 'Invalid JSON'})

        if 'prices' in data and isinstance(data['prices'], str):
            try:
                data['prices'] = json.loads(data['prices'])
            except json.JSONDecodeError:
                raise serializers.ValidationError({'prices': 'Invalid JSON'})

        return super().to_internal_value(data)

    def create(self, validated_data):
        prices_data = validated_data.pop('prices', [])
        images = validated_data.pop('images', [])

        # Create product first
        product = super().create(validated_data)

        # Create prices
        for price_data in prices_data:
            ProductPrice.objects.create(product=product, **price_data)

        # Create images
        for image_file in images:
            img_obj = ProductImage.objects.create(image=image_file)
            product.images.add(img_obj)

        return product