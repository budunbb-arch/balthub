from django.conf import settings
from django.shortcuts import render
from django.urls import resolve, Resolver404
from apps.core.models import SiteSettings
from apps.core.engines.builders import get_default_seo


ALWAYS_ALLOWED_PATHS = [
    settings.STATIC_URL,
    "/admin/",
]

SOFT_DISABLE_ALLOWED_PATHS = [
    "/robots.txt",
    "/sitemap.xml",
    settings.MEDIA_URL,
    "/api/",
    "/feedback/",
]


class SiteStatusMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info
        user = getattr(request, "user", None)

        if user and getattr(user, "is_staff", False):
            return self.get_response(request)

        if any(path.startswith(prefix) for prefix in ALWAYS_ALLOWED_PATHS):
            return self.get_response(request)

        site_settings = SiteSettings.get_solo()

        if site_settings and site_settings.is_fully_disabled:
            response = render(request, "errors/full_maintenance.html", status=503)
            response["Cache-Control"] = "no-store"
            return response

        if any(path.startswith(prefix) for prefix in SOFT_DISABLE_ALLOWED_PATHS):
            return self.get_response(request)

        try:
            resolve(request.path_info)
        except Resolver404:
            return self.get_response(request)

        if site_settings and site_settings.is_disabled:
            seo = get_default_seo(request)
            seo["title"] = f"{seo.get('site_title', '')} | {seo.get('site_name', '')}"
            return render(request, "default/errors/maintenance.html", status=503, context={"seo": seo})

        return self.get_response(request)
