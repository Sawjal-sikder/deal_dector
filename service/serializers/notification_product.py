from rest_framework import serializers # type: ignore
from django.core.cache import cache # type: ignore
from ..models import NotificationProducts # type: ignore
from service.views.products_views import get_all_products_cached # type: ignore
from service.utils.product_matching import product_matching_service # type: ignore
from service.utils.fetch_mysql_data import DB_Query # type: ignore

def get_supermarkets_cached():
    """Cache supermarkets to avoid repeated DB queries"""
    cache_key = 'all_supermarkets_dict'
    supermarket_dict = cache.get(cache_key)

    if supermarket_dict is None:
        query = "SELECT * FROM supermarkets;"
        supermarkets = list(DB_Query(query=query))
        supermarket_dict = {shop['id']: shop for shop in supermarkets}
        cache.set(cache_key, supermarket_dict, timeout=3600)

    return supermarket_dict

class NotificationProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationProducts
        fields = ['id', 'user', 'product_id']
        read_only_fields = ['id','user']
        
        
    def validate(self, attrs):
        user = self.context['request'].user
        product_id = attrs.get('product_id')
        
        if NotificationProducts.objects.filter(user=user, product_id=product_id).exists():
            raise serializers.ValidationError({
                'product_id': 'You have already added this product to notifications.'
            })
        return attrs

        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = instance.user.full_name or instance.user.email
        representation['product_name'] = None
        representation['cheapest_rate_supermarket_name'] = None

        all_products = get_all_products_cached()
        product = next((p for p in all_products if p.get('id') == instance.product_id), None)

        if product:
            representation['product_name'] = product.get('name')
            supermarket_id = product.get('supermarket_id')

            product_match_ids = product_matching_service(
                product_id=instance.product_id,
                supermarket_id=supermarket_id if supermarket_id else 1
            )
            # Get full product details for matched IDs
            product_matches = [
                p for p in all_products if p.get('id') in product_match_ids
            ]

            # Find cheapest product and get supermarket name
            if product_matches:
                cheapest_product = min(product_matches, key=lambda p: p.get('price') or float('inf'))
                supermarket_dict = get_supermarkets_cached()
                cheapest_supermarket = supermarket_dict.get(cheapest_product.get('supermarket_id'), {})
                representation['cheapest_rate_supermarket_name'] = cheapest_supermarket.get('name')

        if not representation['cheapest_rate_supermarket_name']:
            return None

        representation['notification'] = {
            "title": f"'{representation['product_name']}' offer Notification",
            "message": f"'{representation['product_name']}' is most cheapest price in '{representation['cheapest_rate_supermarket_name'].lower()}' supermarket",
        }
        return representation    