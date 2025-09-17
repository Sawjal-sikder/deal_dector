from django.urls import path
from .views import *

urlpatterns = [
    path("generate-recipe/", ChatHistoryView.as_view(), name="generate-recipe"),
    path("chat-history/", ChatHistoryListView.as_view(), name="chat-history"),
    path("recipes/list/", RecipeListView.as_view(), name="recipes"),
]
