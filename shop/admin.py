from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import *

@admin.register(Supershop)
class SupershopAdmin(TranslatableAdmin):
      list_display = ('super_shop_name', 'created_at', 'updated_at')
      
      
      
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')