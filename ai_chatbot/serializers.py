# serializers.py
from rest_framework import serializers

class RecipeRequestSerializer(serializers.Serializer):
    recipe_text = serializers.CharField()
