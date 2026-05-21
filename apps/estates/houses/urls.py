# /opt/balthub/apps/estates/houses/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("ajax/house/<slug:house_slug>/plans/", views.house_plans_ajax, name="house_plans_ajax"),
    path("", views.house_list, name="house_list"),
    path("<slug:project_slug>/<slug:house_slug>/", views.house_detail, name="house_detail"),
]

print("🔥 LOADED HOUSE URLS MODULE")
