# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('supershops/', SupershopListCreateView.as_view(), name='supershop-list-create'),
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('products/', ProductListView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('prices/', ProductPriceCreateView.as_view(), name='product-price-create'),
]
