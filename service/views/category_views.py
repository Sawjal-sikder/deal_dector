from rest_framework.response import Response # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework import permissions # type: ignore
from django.core.cache import cache # type: ignore
import random

from service.utils.fetch_mysql_data import DB_Query


class CategoryMySQLView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        CATEGORIES_CACHE_KEY = "all_categories_data"
        cache_timeout = 60 * 60 * 24  # 24 hours

        # 🔹 Get items param
        items_param = request.query_params.get("items", "5")

        categories = cache.get(CATEGORIES_CACHE_KEY)

        if categories is None:
            query = "SELECT * FROM categories;"
            categories = list(DB_Query(query=query))  # ensure list
            cache.set(CATEGORIES_CACHE_KEY, categories, cache_timeout)

        total_categories = len(categories)

        # 🔹 Logic for items param
        if items_param == "all":
            result_categories = categories
        else:
            try:
                limit = int(items_param)
                limit = max(1, limit)  # avoid 0 or negative
                limit = min(limit, total_categories)  # avoid overflow
                result_categories = random.sample(categories, limit)
            except ValueError:
                # fallback if invalid param
                result_categories = random.sample(
                    categories, min(5, total_categories)
                )

        return Response({
            "total_categories": total_categories,
            "returned_categories": len(result_categories),
            "categories": result_categories
        })
