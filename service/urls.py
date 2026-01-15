from django.urls import path # type: ignore
from .views.products_views import (
    ProductMySQLView,
    RefreshProductsCacheView,
    ProductDetailsView,
    )
from .views.favorite_product_views import (
    FavoriteProductListCreateView,
    FavoriteProductDetailView,
    ) # type: ignore

from .views.notification_product_views import (
    NotificationProductsListCreateView,
    NotificationProductsDeleteView,
    ) # type: ignore
from .views.notification import NotificationView # type: ignore

urlpatterns = [
    path('products/', ProductMySQLView.as_view(), name='products-mysql'),
    path('products/<int:product_id>/', ProductDetailsView.as_view(), name='product-details'),
    path('products/refresh-cache/', RefreshProductsCacheView.as_view(), name='refresh-products-cache'),
    
    # Favorite Product
    path('favorite-products/', FavoriteProductListCreateView.as_view(), name='favorite-products'),
    path('favorite-products/<int:pk>/', FavoriteProductDetailView.as_view(), name='favorite-product-detail'),
    
    
    # Notification Products can be added here in future
    path('notification-products/', NotificationProductsListCreateView.as_view(), name='notification-products'),
    path('notification-products/<int:pk>/', NotificationProductsDeleteView.as_view(), name='notification-product-detail'),
    path('notifications/', NotificationView.as_view(), name='notifications'),
    
]