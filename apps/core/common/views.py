# apps/core/common/views.py

from django.shortcuts import render
from django.core.cache import cache
from apps.estates.projects.models import Project


def home(request):
    cache_key = "home_page"

    request.layout = {
        "main_menu": ["default/modules/main_menu.html"],
        "account_menu": ["default/modules/account_menu.html"],
        # без sidebar
    }

    return render(request, "default/pages/common/home.html", {
        
    })
