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
        fields = [
            'id', 'translations', 'category',
            'product_image1', 'product_image2', 'product_image3',
            'uom', 'prices'
        ]

    def to_internal_value(self, data):
        data = data.copy() if hasattr(data, 'copy') else data

        if hasattr(data, 'getlist'):  # Handle QueryDict
            converted_data = {}
            for key in data.keys():
                values = data.getlist(key)
                converted_data[key] = values[0] if values else ''
            data = converted_data

        if 'translations' in data and isinstance(data['translations'], str):
            try:
                data['translations'] = json.loads(data['translations'])
            except json.JSONDecodeError:
                raise serializers.ValidationError({'translations': 'Invalid JSON format'})

        if 'prices' in data and isinstance(data['prices'], str):
            try:
                data['prices'] = json.loads(data['prices'])
            except json.JSONDecodeError:
                raise serializers.ValidationError({'prices': 'Invalid JSON format'})

        return super().to_internal_value(data)

    def validate_translations(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Translations must be a dictionary")
        if 'en' not in value:
            raise serializers.ValidationError("English translation is required")

        en_fields = value['en']
        if not isinstance(en_fields, dict):
            raise serializers.ValidationError("English translation must be a dictionary")

        if 'product_name' not in en_fields:
            raise serializers.ValidationError("English product_name is required")

        if 'description' not in en_fields:
            raise serializers.ValidationError("English description is required")

        for lang_code, fields in value.items():
            if not isinstance(fields, dict):
                raise serializers.ValidationError(
                    f"Language '{lang_code}' should contain field dictionary"
                )
        return value

    def create(self, validated_data):
        prices_data = validated_data.pop('prices', [])
        product = Product.objects.create(**validated_data)
        for price_data in prices_data:
            ProductPrice.objects.create(product=product, **price_data)
        return product

    def update(self, instance, validated_data):
        # Pop nested prices data
        prices_data = validated_data.pop('prices', [])

        # Update Product main fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update prices - preserve existing prices and update them instead of deleting
        if prices_data:
            for price_data in prices_data:
                shop_id = price_data.get('shop')
                price_value = price_data.get('price')
                
                if shop_id and price_value is not None:
                    # Try to get existing price record
                    existing_price = instance.prices.filter(shop_id=shop_id).first()
                    
                    if existing_price:
                        # Update existing price (this will trigger the signal)
                        existing_price.price = price_value
                        existing_price.save()
                    else:
                        # Create new price record
                        ProductPrice.objects.create(
                            product=instance, 
                            shop_id=shop_id, 
                            price=price_value
                        )

        return instance

    def delete(self, instance):
        """
        Optional: handle deletion via serializer.
        Usually this is handled in the viewset, but you can use this
        if you want to call serializer.delete(instance).
        """
        instance.delete()
        return instance






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
        
       
# product list of category wise products
class ProductListbyCategoryByShopSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=Product)
    prices = serializers.SerializerMethodField()  # override to filter by shop_ids

    class Meta:
        model = Product
        fields = "__all__"

    def get_prices(self, obj):
        shop_ids = self.context.get("shop_ids")
        qs = obj.prices.all()
        if shop_ids:
            qs = qs.filter(shop_id__in=shop_ids)
        return ProductPriceUseListSerializer(qs, many=True).data


# Product list by shop wise products
class CategoryProductsByShopSerializer(serializers.ModelSerializer):
    products = ProductListbyCategoryByShopSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'category_name', 'products']

       
# favorites serializers   
class FavoriteCreateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = "__all__"

class FavoriteListSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'product']
       
# Wishlist serializers   
class WishlistCreateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = "__all__"

class WishlistListSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'product']

# ShoppingList serializers
class ShoppingListCreateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingList
        fields = "__all__"

class ShoppingListListSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = ShoppingList
        fields = ['id', 'user', 'product']
        
        
        
class NotificationSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "product", "product_name", "message", "is_read", "created_at"]
        
class UseNotificationSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "product_name", "message", "is_read", "created_at"]