from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework import permissions # type: ignore
from rest_framework.pagination import PageNumberPagination # type: ignore
from ..utils.fetch_mysql_data import DB_Query

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # default page size
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductMySQLView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        search = request.query_params.get('search', '')
        category_id = request.query_params.get('category_id', '')

        # Build query with filters
        conditions = []
        params = []

        if search:
            conditions.append("name LIKE %s")
            params.append(f"%{search}%")

        if category_id:
            conditions.append("category_id = %s")
            params.append(category_id)

        if conditions:
            query = f"SELECT * FROM products WHERE {' AND '.join(conditions)};"
            data = DB_Query(query=query, params=tuple(params))
        else:
            query = "SELECT * FROM products;"
            data = DB_Query(query=query)

        # Paginate the result using DRF paginator
        paginator = StandardResultsSetPagination()
        paginated_data = paginator.paginate_queryset(data, request)

        return paginator.get_paginated_response(paginated_data)



