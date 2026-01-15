from django.urls import path # type: ignore
from .views.products_views import (
    ProductMySQLView,
    )

urlpatterns = [
    path('products/', ProductMySQLView.as_view(), name='products-mysql'),
]