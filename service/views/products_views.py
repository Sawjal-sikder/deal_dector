import logging

from rest_framework.views import APIView  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework import permissions, status  # type: ignore
from rest_framework.pagination import PageNumberPagination  # type: ignore

from django.core.cache import cache  # type: ignore
from django.conf import settings  # type: ignore

from ..utils.fetch_mysql_data import DB_Query
from ..tasks import PRODUCTS_CACHE_KEY

logger = logging.getLogger(__name__)


# =========================
# Cache config
# =========================
PRODUCTS_CACHE_TIMEOUT = getattr(
    settings, 'PRODUCTS_CACHE_TIMEOUT', 86400
)  # 24 hours


# =========================
# Pagination
# =========================
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100000000


# =========================
# Cache helper
# =========================
def get_all_products_cached():
    """
    Fetch all products from cache or MySQL.
    Cache is populated on first request.
    Returns None if database query fails.
    """
    data = cache.get(PRODUCTS_CACHE_KEY)
    if data is None:
        try:
            query = "SELECT * FROM products;"
            data = DB_Query(query=query, read_timeout=600)
            cache.set(PRODUCTS_CACHE_KEY, data, PRODUCTS_CACHE_TIMEOUT)
        except Exception as e:
            logger.error(f"Failed to fetch products from database: {e}")
            return None
    return data


# =========================
# In-memory filters
# =========================
def filter_products(data, search='', category_id='', supermarket_id=''):
    """
    Filter products in memory by:
    - category_id
    - supermarket_id
    - search (product name)
    """
    filtered_data = data

    # ---- category filter ----
    if category_id:
        try:
            category_id = int(category_id)
            filtered_data = [
                p for p in filtered_data
                if p.get('category_id') == category_id
            ]
        except (ValueError, TypeError):
            pass

    # ---- supermarket filter ----
    if supermarket_id:
        try:
            supermarket_id = int(supermarket_id)
            filtered_data = [
                p for p in filtered_data
                if p.get('supermarket_id') == supermarket_id
            ]
        except (ValueError, TypeError):
            pass

    # ---- search filter ----
    if search:
        search = search.lower()
        filtered_data = [
            p for p in filtered_data
            if search in (p.get('name') or '').lower()
        ]

    return filtered_data


# =========================
# Product list view
# =========================
class ProductMySQLView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        search = request.query_params.get('search', '')
        category_id = request.query_params.get('category_id', '')
        supermarket_id = request.query_params.get('supermarket_id', '')

        # Fetch cached products
        all_products = get_all_products_cached()

        if all_products is None:
            return Response(
                {'error': 'Service temporarily unavailable. Please try again later.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # Apply filters
        filtered_products = filter_products(
            all_products,
            search=search,
            category_id=category_id,
            supermarket_id=supermarket_id,
        )

        # Sort by updated_at (most recent first)
        filtered_products = sorted(
            filtered_products,
            key=lambda p: p.get('updated_at') or '',
            reverse=True
        )

        # Pagination
        paginator = StandardResultsSetPagination()
        paginated_data = paginator.paginate_queryset(
            filtered_products, request
        )

        return paginator.get_paginated_response(paginated_data)


# =========================
# Product details view
# =========================
class ProductDetailsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, product_id):
        all_products = get_all_products_cached()

        if all_products is None:
            return Response(
                {'error': 'Service temporarily unavailable. Please try again later.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # IMPORTANT: product_id comes as string → convert to int
        try:
            product_id = int(product_id)
        except ValueError:
            return Response({'error': 'Invalid product id'}, status=400)

        product = next(
            (p for p in all_products if p.get('id') == product_id),
            None
        )

        if product:
            return Response(product)

        return Response({'error': 'Product not found'}, status=404)


# =========================
# Manual cache refresh
# =========================
class RefreshProductsCacheView(APIView):
    """
    Admin-only endpoint to refresh product cache.
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        cache.delete(PRODUCTS_CACHE_KEY)
        get_all_products_cached()  # re-cache
        return Response(
            {'message': 'Products cache refreshed successfully'}
        )
