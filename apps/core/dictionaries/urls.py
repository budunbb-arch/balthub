# apps/core/dictionaries/urls.py

from django.urls import path
from .views import districts_by_city

urlpatterns = [
    path("districts/", districts_by_city, name="districts_by_city"),
]
