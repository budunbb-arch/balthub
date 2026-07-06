from django.conf import settings
from django.shortcuts import render
from django.urls import resolve, Resolver404
from apps.core.models import SiteSettings


ALLOWED_SITE_DISABLED_PATHS = [
    settings.STATIC_URL,
    settings.MEDIA_URL,
    "/admin/",
    "/api/",
]


class SiteStatusMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info

        if any(path.startswith(prefix) for prefix in ALLOWED_SITE_DISABLED_PATHS):
            return self.get_response(request)

        try:
            resolve(request.path_info)
        except Resolver404:
            return self.get_response(request)

        site_settings = SiteSettings.get_solo()
        user = getattr(request, "user", None)

        if site_settings and site_settings.is_disabled and not (user and getattr(user, "is_staff", False)):
            return render(request, "default/errors/maintenance.html", status=503)

        return self.get_response(request)
