# apps/estates/developers/urls.py

from django.urls import path
from .views import developer_detail, developer_list
from .api import developer_detail_api

urlpatterns = [
    path("", developer_list, name="developer_list"),
    path("<slug:slug>/", developer_detail, name="developer_detail"),
    path("<slug:slug>/api/", developer_detail_api, name="developer_detail_api"),
]