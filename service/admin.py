from django.contrib import admin # type: ignore
from .models import FavoriteProduct # type: ignore

@admin.register(FavoriteProduct)
class FavoriteProductAdmin(admin.ModelAdmin):
    list_display = ('user', 'product_id', 'created_at', 'updated_at')
    search_fields = ('user__username', 'product_id')
    list_filter = ('created_at', 'updated_at')