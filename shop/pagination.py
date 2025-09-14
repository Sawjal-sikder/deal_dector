from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # default items per page
    page_size_query_param = 'per_page'  # frontend can change this via query param
    max_page_size = 100  # optional maximum limit
