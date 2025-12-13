from django.urls import path
from .views import *

urlpatterns = [
    
    path('tables/', AllTablesMySQLView.as_view(), name='mysql-table-list'),
    path("products/", ProductMySQLView.as_view(), name="product-mysql-list"),
    path('product-discounts/', CurrentDiscountsMySQLView.as_view(), name='current-discounts-products'),
    path('product-discounts/<int:product_id>/', ProductDetailsMySQLView.as_view(), name='product-discounts'),
    
    # Category MySQL fetch
    path('categories/', CategoryMySQLView.as_view(), name='category-mysql-list'),
    
    # Supermarket MySQL fetch
    path('supermarkets/', SupermarketMySQLView.as_view(), name='supermarket-mysql-list'),
    
    
    
    
    # Category wise products MySQL fetch
    path('category-products/', CategoryWiseProductsMySQLView.as_view(), name='category-wise-products-mysql'),
    
    # favorite products
    path('favorites/', FavoriteView.as_view(), name='favorite-list'),
    path('favorites/<int:product_id>/', FavoriteCreateDeleteView.as_view(), name='favorite-create-delete'),
    
    # wishlist products
    path('wishlists/<product_id>/', WishlistCreateDeleteView.as_view(), name='wishlist-create-delete'),
    path('wishlists/', WishlistView.as_view(), name='wishlist-list'),
    
    
    # ShoppingList products
    # path('shopping-lists/create/', ShoppingListCreateDeleteView.as_view(), name='shopping-list-create'),
    path('shopping-lists/<product_id>/', ShoppingListCreateDeleteView.as_view(), name='shopping-list-create-delete'),
    path('shopping-lists/', ShoppingListView.as_view(), name='shopping-list-list'),
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    path('supershops/', SupershopListCreateView.as_view(), name='supershop-list-create'),
    path('supershops/<int:pk>/', SupershopDetailView.as_view(), name='supershop-detail'),
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('products/', ProductListView.as_view(), name='product-list-create'),
    path('products/list/', ProductView.as_view(), name='product-list'),
    path('products/details/<int:pk>/', ProductDetailsonlyView.as_view(), name='product-detail'),
    path('products/update-delete/<int:pk>/', ProductUpdateDeleteView.as_view(), name='product-update-delete'),
    path('category-products/<int:category_id>/', CategoryByProductsView.as_view(), name='category-products'),
    path('category-products/', CategoryByProductsView.as_view(), name='category-products'),
    path("category-products/shop/<str:shop_ids>/", CategoryByProductsByShopView.as_view(), name="category-products"),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('prices/', ProductPriceCreateView.as_view(), name='product-price-create'),
    path('prices/<int:pk>/', ProductPriceUpdateView.as_view(), name='product-price-update'),
    

    


    # Notification system
    path('subscribe/<int:product_id>/', ToggleSubscriptionView.as_view(), name='product-subscribe-unsubscribe'),
    path('notifications/', UserNotificationsView.as_view(), name='notification-list'),
    path('notifications/use/<int:pk>/', UseNotificationsView.as_view(), name='notification-use'),

    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # use promo code
    path('promo-code/use/', UsePromoCodeView.as_view(), name='use-promo-code')
]
