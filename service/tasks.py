from celery import shared_task #type: ignore
from django.core.cache import cache # type: ignore
from .utils.fetch_mysql_data import DB_Query
from django.conf import settings # type: ignore

PRODUCTS_CACHE_KEY = "all_products_data"
BATCH_SIZE = 10000


@shared_task
def refresh_products_cache():

    cache_timeout = getattr(settings, "PRODUCTS_CACHE_TIMEOUT", 86400)

    # ✅ Step 1: Delete old cache
    cache.delete(PRODUCTS_CACHE_KEY)

    last_id = 0
    all_products = []

    while True:
        query = f"""
            SELECT *
            FROM products
            WHERE id > {last_id}
            ORDER BY id ASC
            LIMIT {BATCH_SIZE}
        """

        batch_data = DB_Query(query=query)

        if not batch_data:
            break

        all_products.extend(batch_data)

        last_id = batch_data[-1]["id"]

    # ✅ Step 2: Save new cache
    cache.set(PRODUCTS_CACHE_KEY, all_products, cache_timeout)

    return f"Products cache refreshed. {len(all_products)} products cached."
