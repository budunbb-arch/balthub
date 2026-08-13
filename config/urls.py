# /opt/balthub/config/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from apps.core.common.views import home
from apps.core.documents.views import documents_list, document_detail, document_modal
from apps.core.sitemap import SitemapView
from apps.core.robots import RobotsView
from apps.leads.views import feedback_send


urlpatterns = [
    path("", home, name="home"),
    path("sitemap.xml", SitemapView.as_view(), name="sitemap"),
    path("robots.txt", RobotsView.as_view(), name="robots"),
    path("admin/", admin.site.urls),
    path("estates/", include("apps.estates.urls")),
    path("api/", include("apps.core.dictionaries.urls")),
    path("documents/", documents_list, name="documents"),
    path("documents/<int:document_id>/", document_detail, name="document_detail"),
    path("documents/modal/<int:document_id>/", document_modal, name="document_modal"),
    path("feedback/send/", feedback_send, name="feedback_send"),
]

#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler403 = "apps.core.common.views.error_403"
handler404 = "apps.core.common.views.error_404"
handler500 = "apps.core.common.views.error_500"