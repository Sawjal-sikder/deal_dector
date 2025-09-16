from django.urls import path
from .views import GenerateRecipeView

urlpatterns = [
    path("generate-recipe/", GenerateRecipeView.as_view(), name="generate-recipe"),
]
