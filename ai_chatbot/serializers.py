from .models import *
from rest_framework import serializers

class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        fields = "__all__"
        read_only_fields = ['response_data', 'user', 'flag', 'created_at']
        
        
        
class ChatHistoryListSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = ChatHistory
        fields = ['id', 'user', 'request_data', 'response_data', 'created_at']
        
        
class RecipeListSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = ChatHistory
        fields = ['id', 'user', 'flag', 'request_data', 'response_data', 'created_at']
