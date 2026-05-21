from django.urls import path
from .views import flat_detail

urlpatterns = [
    path("<slug:project_slug>/<slug:house_slug>/<slug:flat_slug>/", flat_detail, name="flat_detail"),
]
