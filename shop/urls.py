# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('supershops/', SupershopListCreateView.as_view(), name='supershop-list-create'),
    path('supershops/<int:pk>/', SupershopDetailView.as_view(), name='supershop-detail'),
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('products/', ProductListView.as_view(), name='product-list-create'),
    path('products/list/', ProductView.as_view(), name='product-list'),
    path('products/details/<int:pk>/', ProductDetailsonlyView.as_view(), name='product-detail'),
    path('category-products/', CategoryProductsView.as_view(), name='category-products'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('prices/', ProductPriceCreateView.as_view(), name='product-price-create'),
    path('favorites/<product_id>/', FavoriteCreateDeleteView.as_view(), name='favorite-create-delete'),
    path('favorites/', FavoriteView.as_view(), name='favorite-list'),
]
