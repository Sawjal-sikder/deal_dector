from django.contrib import admin
from .models import ChatHistory

@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'request_data', 'response_data')
    list_filter = ('user', 'created_at')
    search_fields = ('user__username', 'request_data', 'response_data')
    readonly_fields = ('created_at',)
