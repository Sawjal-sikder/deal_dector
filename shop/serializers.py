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


class CategoryUseListSerializer(serializers.ModelSerializer):
    translations = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'translations']

    def get_translations(self, obj):
        data = {}
        for trans in obj.translations.all():
            data[trans.language_code] = {
                "category_name": trans.category_name
            }
        return data


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

class ProductPriceUseListSerializer(serializers.ModelSerializer):
    shop = serializers.CharField(source='shop.super_shop_name', read_only=True)
    class Meta:
        model = ProductPrice
        fields = ['id', 'shop', 'price']


class ProductPriceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPrice
        fields = ['shop', 'price']

# Product List Serializer only for listing products
class ProductListSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Product)
    prices = ProductPriceUseListSerializer(many=True, required=False)
    category = CategoryUseListSerializer(read_only=True)

    class Meta:
        model = Product
        # fields = ['id', 'translations', 'category', 'product_image1', 'product_image2', 'product_image3', 'uom', 'prices']
        fields = "__all__"

# create product serializer
class ProductSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Product)
    prices = ProductPriceCreateSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = ['id', 'translations', 'category', 'product_image1', 'product_image2', 'product_image3', 'uom', 'prices']

    def to_internal_value(self, data):
        """
        Handle both JSON and form data submissions for translations.
        """
        data = data.copy() if hasattr(data, 'copy') else data
        
        # Debug: Print incoming data
        # print(f"DEBUG: Incoming data type: {type(data)}")
        # print(f"DEBUG: Incoming data: {dict(data) if hasattr(data, 'items') else data}")
        
        # Handle QueryDict (form data) - extract first value from lists
        if hasattr(data, 'getlist'):
            # Convert QueryDict to regular dict with single values
            converted_data = {}
            for key in data.keys():
                values = data.getlist(key)
                converted_data[key] = values[0] if values else ''
            data = converted_data
            # print(f"DEBUG: Converted QueryDict to: {data}")
        
        # Handle translations field - parse JSON string if needed
        if 'translations' in data and isinstance(data['translations'], str):
            try:
                data['translations'] = json.loads(data['translations'])
                # print(f"DEBUG: Parsed translations successfully")
            except json.JSONDecodeError:
                raise serializers.ValidationError({'translations': 'Invalid JSON format'})
        
        # Handle prices field - parse JSON string if needed
        if 'prices' in data and isinstance(data['prices'], str):
            try:
                original_prices = data['prices']
                data['prices'] = json.loads(data['prices'])
                # print(f"DEBUG: Parsed prices from '{original_prices}' to {data['prices']}")
            except json.JSONDecodeError:
                # print(f"DEBUG: Failed to parse prices JSON: {data['prices']}")
                raise serializers.ValidationError({'prices': 'Invalid JSON format'})
        elif 'prices' in data:
            print(f"DEBUG: Prices field exists but is not string: {data['prices']} (type: {type(data['prices'])})")
        else:
            print(f"DEBUG: No prices field found in data")
        
        result = super().to_internal_value(data)
        # print(f"DEBUG: After validation, result has prices: {'prices' in result}")
        if 'prices' in result:
            print(f"DEBUG: Prices in result: {result['prices']} (count: {len(result['prices'])})")
        return result

    def validate_translations(self, value):
        """
        Validate translations structure and required fields.
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("Translations must be a dictionary")
        
        # Check if English translation exists and has required fields
        if 'en' not in value:
            raise serializers.ValidationError("English translation is required")
        
        en_fields = value['en']
        if not isinstance(en_fields, dict):
            raise serializers.ValidationError("English translation must be a dictionary")
        
        if 'product_name' not in en_fields:
            raise serializers.ValidationError("English product_name is required")
        
        if 'description' not in en_fields:
            raise serializers.ValidationError("English description is required")
        
        # Validate structure for all languages
        for lang_code, fields in value.items():
            if not isinstance(fields, dict):
                raise serializers.ValidationError(f"Language '{lang_code}' should contain field dictionary")
        
        return value
        
    def create(self, validated_data):
        prices_data = validated_data.pop('prices', [])
        product = Product.objects.create(**validated_data)
        for price_data in prices_data:
            ProductPrice.objects.create(product=product, **price_data)
        return product





# product list of category wise products
class ProductListbyCategorySerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Product)
    prices = ProductPriceUseListSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = "__all__"

class CategoryProductsSerializer(serializers.ModelSerializer):
    products = ProductListbyCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'category_name', 'products']
       