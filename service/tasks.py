from celery import shared_task
from django.core.cache import cache

PRODUCTS_CACHE_KEY = 'all_products_data'


@shared_task
def refresh_products_cache():
    """Celery task to refresh the products cache every 24 hours."""
    from .utils.fetch_mysql_data import DB_Query
    from django.conf import settings
    
    # Delete old cache
    cache.delete(PRODUCTS_CACHE_KEY)
    
    # Re-fetch and cache
    query = "SELECT * FROM products;"
    data = DB_Query(query=query)
    cache_timeout = getattr(settings, 'PRODUCTS_CACHE_TIMEOUT', 86400)
    cache.set(PRODUCTS_CACHE_KEY, data, cache_timeout)
    
    return f"Products cache refreshed. {len(data)} products cached."
