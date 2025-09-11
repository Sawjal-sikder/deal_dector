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
        data = data.copy() 
        if 'translations' in data and isinstance(data['translations'], str):
            try:
                data['translations'] = json.loads(data['translations'])
            except json.JSONDecodeError:
                raise serializers.ValidationError({'translations': 'Invalid JSON format'})
        return super().to_internal_value(data)

class SupershopUpdateSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Supershop)

    class Meta:
        model = Supershop
        fields = ['id', 'translations', 'image', 'created_at', 'updated_at']

    def to_internal_value(self, data):
        """
        Handle both JSON and form data submissions for translations.
        """
        data = data.copy() if hasattr(data, 'copy') else data
        
        # Handle translations field - parse JSON string if needed
        if 'translations' in data and isinstance(data['translations'], str):
            try:
                data['translations'] = json.loads(data['translations'])
            except json.JSONDecodeError:
                raise serializers.ValidationError({'translations': 'Invalid JSON format'})
        
        # If request data looks like a translations dict without 'translations' key, wrap it
        if isinstance(data, dict) and "translations" not in data and any(
            key in ['en', 'nl', 'fr', 'es', 'de'] for key in data.keys()
        ):
            data = {"translations": data}

        return super().to_internal_value(data)

    def validate_translations(self, value):
        request_method = self.context.get('request', {}).method if self.context.get('request') else 'PATCH'
        
        if request_method == 'POST':
            # enforce required fields for POST
            if 'en' not in value or 'super_shop_name' not in value['en']:
                raise serializers.ValidationError("English super_shop_name is required.")
        
        # For PATCH, validate structure if provided
        if isinstance(value, dict):
            for lang_code, fields in value.items():
                if not isinstance(fields, dict):
                    raise serializers.ValidationError(f"Language '{lang_code}' should contain field dictionary")
                    
        return value
        return value


class CategorySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Category)

    class Meta:
        model = Category
        fields = "__all__"

    def to_internal_value(self, data):
        data = data.copy()
        if 'translations' in data and isinstance(data['translations'], str):
            try:
                data['translations'] = json.loads(data['translations'])
            except json.JSONDecodeError:
                raise serializers.ValidationError({'translations': 'Invalid JSON format'})
        return super().to_internal_value(data)
    
class CategoryUpdateSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Category)

    class Meta:
        model = Category
        fields = "__all__"

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else data
        
        # Handle translations field - parse JSON string if needed
        if 'translations' in data and isinstance(data['translations'], str):
            try:
                data['translations'] = json.loads(data['translations'])
            except json.JSONDecodeError:
                raise serializers.ValidationError({'translations': 'Invalid JSON format'})
        
        # If request data looks like a translations dict without 'translations' key, wrap it
        if isinstance(data, dict) and "translations" not in data and any(
            key in ['en', 'nl', 'fr', 'es', 'de'] for key in data.keys()
        ):
            data = {"translations": data}

        return super().to_internal_value(data)

    def validate_translations(self, value):
        request_method = self.context.get('request', {}).method if self.context.get('request') else 'PATCH'
        
        if request_method == 'POST':
            # enforce required fields for POST
            if 'en' not in value or 'category_name' not in value['en']:
                raise serializers.ValidationError("English category_name is required.")
        
        # For PATCH, validate structure if provided
        if isinstance(value, dict):
            for lang_code, fields in value.items():
                if not isinstance(fields, dict):
                    raise serializers.ValidationError(f"Language '{lang_code}' should contain field dictionary")
                    
        return value

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