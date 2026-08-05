# apps/core/common/views.py

from django.shortcuts import render
from django.core.cache import cache
from apps.estates.projects.models import Project


def home(request):
    cache_key = "home_page"

    return render(request, "default/pages/common/home.html", {
        "is_home": True,
    })


def error_403(request, exception):

    return render(
        request,
        "default/errors/403.html",
        status=403
    )


def error_404(request, exception):

    return render(
        request,
        "default/errors/404.html",
        status=404
    )


def error_500(request):

    return render(
        request,
        "default/errors/500.html",
        status=500
    )