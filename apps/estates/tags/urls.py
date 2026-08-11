# apps/estates/tags/urls.py

from django.urls import path
from .views import tag_list, tag_detail

urlpatterns = [
    path("", tag_list, name="tag_list"),
    path("<slug:tag_slug>/", tag_detail, name="tag_detail"),
]
