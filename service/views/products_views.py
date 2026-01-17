from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework import permissions # type: ignore
from rest_framework.pagination import PageNumberPagination # type: ignore
from django.core.cache import cache
from django.conf import settings
from ..utils.fetch_mysql_data import DB_Query
from ..tasks import PRODUCTS_CACHE_KEY

PRODUCTS_CACHE_TIMEOUT = getattr(settings, 'PRODUCTS_CACHE_TIMEOUT', 86400)  # 24 hours default

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # default page size
    page_size_query_param = 'page_size'
    max_page_size = 100


def get_all_products_cached():
    """Fetch all products from cache or database."""
    data = cache.get(PRODUCTS_CACHE_KEY)
    if data is None:
        query = "SELECT * FROM products;"
        data = DB_Query(query=query)
        cache.set(PRODUCTS_CACHE_KEY, data, PRODUCTS_CACHE_TIMEOUT)
    return data


def filter_products(data, search='', category_id=''):
    """Filter products in memory based on search and category_id."""
    filtered_data = data
    
    if category_id:
        try:
            category_id_int = int(category_id)
            filtered_data = [p for p in filtered_data if p.get('category_id') == category_id_int]
        except (ValueError, TypeError):
            pass
    
    if search:
        search_lower = search.lower()
        filtered_data = [p for p in filtered_data if search_lower in (p.get('name', '') or '').lower()]
    
    return filtered_data


class ProductMySQLView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        search = request.query_params.get('search', '')
        category_id = request.query_params.get('category_id', '')

        # Get all products from cache (loads from DB on first request)
        all_products = get_all_products_cached()
        
        # Filter in memory
        data = filter_products(all_products, search=search, category_id=category_id)

        # Paginate the result using DRF paginator
        paginator = StandardResultsSetPagination()
        paginated_data = paginator.paginate_queryset(data, request)

        return paginator.get_paginated_response(paginated_data)
    
    
class ProductDetailsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, product_id):
        all_products = get_all_products_cached()
        product = next((p for p in all_products if p.get('id') == product_id), None)
        if product:
            return Response(product)
        return Response({'error': 'Product not found'}, status=404)


class RefreshProductsCacheView(APIView):
    """Endpoint to manually refresh the products cache."""
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        cache.delete(PRODUCTS_CACHE_KEY)
        # Re-fetch and cache
        get_all_products_cached()
        return Response({'message': 'Products cache refreshed successfully'})



