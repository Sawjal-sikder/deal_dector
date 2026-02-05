from rest_framework import serializers # type: ignore
from django.core.cache import cache # type: ignore
from ..models import Notification # type: ignore
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

class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ['id', 'title', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

   
        
        
    