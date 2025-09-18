from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import *

@admin.register(Supershop)
class SupershopAdmin(TranslatableAdmin):
      list_display = ('super_shop_name', 'created_at', 'updated_at')
      
      
      
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')


@admin.register(ProductSubscription)
class ProductSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'message', 'is_read', 'created_at')