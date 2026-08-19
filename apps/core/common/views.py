# apps/core/common/views.py

from django.shortcuts import render
from django.core.cache import cache
from apps.estates.projects.models import Project
from apps.core.engines.builders import get_default_seo


def home(request):
    cache_key = "home_page"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    response = render(request, "default/pages/common/home.html", {
        "is_home": True,
    })
    cache.set(cache_key, response, 300)
    return response


def error_403(request, exception):
    seo = get_default_seo(request)
    seo["title"] = f"403 - {seo.get('site_title', '')}"
    seo["site_name"] = seo.get("site_name", "")
    seo["site_title"] = seo.get("site_title", "")

    return render(
        request,
        "default/errors/403.html",
        status=403,
        context={"seo": seo}
    )


def error_404(request, exception):
    seo = get_default_seo(request)
    seo["title"] = f"404 - {seo.get('site_title', '')}"
    seo["site_name"] = seo.get("site_name", "")
    seo["site_title"] = seo.get("site_title", "")

    return render(
        request,
        "default/errors/404.html",
        status=404,
        context={"seo": seo}
    )


def error_500(request):
    seo = get_default_seo(request)
    seo["title"] = f"500 - {seo.get('site_title', '')}"
    seo["site_name"] = seo.get("site_name", "")
    seo["site_title"] = seo.get("site_title", "")

    return render(
        request,
        "default/errors/500.html",
        status=500,
        context={"seo": seo}
    )