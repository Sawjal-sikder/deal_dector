# urls.py
from django.urls import path
from .views import SupershopListCreateView

urlpatterns = [
    path('supershops/', SupershopListCreateView.as_view(), name='supershop-list-create'),
]
