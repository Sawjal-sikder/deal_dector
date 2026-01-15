from django.urls import path # type: ignore
from .views.products_views import (
    ProductMySQLView,
    RefreshProductsCacheView,
    )

urlpatterns = [
    path('products/', ProductMySQLView.as_view(), name='products-mysql'),
    path('products/refresh-cache/', RefreshProductsCacheView.as_view(), name='refresh-products-cache'),
]