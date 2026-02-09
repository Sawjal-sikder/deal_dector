from django.urls import path # type: ignore

from service.views.category_views import CategoryMySQLView
from service.views.purchased_list_views import PurchasedListDeleteView, PurchasedListView, TotalPurchasePriceView
from service.views.supershop_views import SuperShopMySQLView # type: ignore
from .views.selected_supermarket_views import SelectedSupermarketDetailView, SelectedSupermarketListCreateView # type: ignore
from service.views.product_details_views import ProductDetailsView  # type: ignore
from .views.products_views import (
    ProductMySQLView,
    RefreshProductsCacheView,
    )
from .views.favorite_product_views import (
    FavoriteProductListCreateView,
    FavoriteProductDetailView,
    ) # type: ignore

from .views.notification_product_views import (
    NotificationDetailView,
    NotificationView,
    ) # type: ignore
from .views.shopping_views import (
    ListShoppingView,
    ShoppingListCreateView,
    ShoppingDetailView,
) # type: ignore

urlpatterns = [
    # categories
    path('categories/', CategoryMySQLView.as_view(), name='categories-mysql'),
    
    # supermarkets
    path('supermarkets/', SuperShopMySQLView.as_view(), name='supermarkets-mysql'),
    
    # Products
    path('products/', ProductMySQLView.as_view(), name='products-mysql'),
    path('products/<int:product_id>/', ProductDetailsView.as_view(), name='product-details'),
    path('products/refresh-cache/', RefreshProductsCacheView.as_view(), name='refresh-products-cache'),
    
    # Favorite Product
    path('favorite-products/', FavoriteProductListCreateView.as_view(), name='favorite-products'),
    path('favorite-products/<int:pk>/', FavoriteProductDetailView.as_view(), name='favorite-product-detail'),
    

    
    # Notification Products can be added here in future
    # path('notification/', NotificationProductsListCreateView.as_view(), name='notification-products'),
    path('notifications/', NotificationView.as_view(), name='notifications'),
    path('notification/<int:pk>/', NotificationDetailView.as_view(), name='notification-product-detail'),
    
    # Shopping can be added here in future
    path('shopping/list/', ListShoppingView.as_view(), name='shopping-list'),
    path('shopping/', ShoppingListCreateView.as_view(), name='shopping-list-create'),
    path('shopping/<int:product_id>/', ShoppingDetailView.as_view(), name='shopping-detail'),
    
    # purchased products
    path('purchased/', PurchasedListView.as_view(), name='purchased-list'),
    path('purchased/delete/', PurchasedListDeleteView.as_view(), name='purchased-list-delete'),
    path('purchased/total-price/', TotalPurchasePriceView.as_view(), name='total-purchase-price'),
    
    # supermarket selection can be added here in future
    path('selected-supermarkets/', SelectedSupermarketListCreateView.as_view(), name='selected-supermarkets'),
    path('selected-supermarkets/<int:pk>/', SelectedSupermarketDetailView.as_view(), name='selected-supermarket-detail'),
]