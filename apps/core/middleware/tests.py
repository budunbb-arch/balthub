from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase

from apps.core.middleware.site_status import SiteStatusMiddleware


class SiteStatusMiddlewareTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.get_response = Mock(return_value=HttpResponse("site"))
        self.middleware = SiteStatusMiddleware(self.get_response)

    def make_request(self, path, user=None):
        request = self.factory.get(path)
        request.user = user or AnonymousUser()
        return request

    @patch("apps.core.middleware.site_status.SiteSettings.get_solo")
    def test_full_disable_shows_standalone_maintenance_page_for_all_public_paths(
        self, get_site_settings
    ):
        get_site_settings.return_value = SimpleNamespace(
            is_fully_disabled=True,
            is_disabled=False,
        )

        for path in (
            "/",
            "/feedback/send/",
            "/api/",
            f"{settings.MEDIA_URL}images/house.jpg",
            "/unknown/",
        ):
            with self.subTest(path=path):
                response = self.middleware(self.make_request(path))

                self.assertEqual(response.status_code, 503)
                self.assertContains(response, "Сайт временно недоступен", status_code=503)

        self.get_response.assert_not_called()

    @patch("apps.core.middleware.site_status.SiteSettings.get_solo")
    def test_staff_user_can_view_site_during_full_disable(self, get_site_settings):
        request = self.make_request("/private-preview/", SimpleNamespace(is_staff=True))

        response = self.middleware(request)

        self.assertEqual(response.status_code, 200)
        self.get_response.assert_called_once_with(request)
        get_site_settings.assert_not_called()

    @patch("apps.core.middleware.site_status.SiteSettings.get_solo")
    def test_admin_and_static_paths_remain_available_during_full_disable(
        self, get_site_settings
    ):
        get_site_settings.return_value = SimpleNamespace(
            is_fully_disabled=True,
            is_disabled=False,
        )

        for path in ("/admin/login/", f"{settings.STATIC_URL}admin/css/base.css"):
            with self.subTest(path=path):
                response = self.middleware(self.make_request(path))
                self.assertEqual(response.status_code, 200)

        get_site_settings.assert_not_called()
        self.assertEqual(self.get_response.call_count, 2)

    @patch("apps.core.middleware.site_status.render")
    @patch("apps.core.middleware.site_status.get_default_seo")
    @patch("apps.core.middleware.site_status.SiteSettings.get_solo")
    def test_soft_disable_keeps_feedback_available_and_shows_existing_page(
        self, get_site_settings, get_default_seo, render
    ):
        get_site_settings.return_value = SimpleNamespace(
            is_fully_disabled=False,
            is_disabled=True,
        )
        render.return_value = HttpResponse("soft maintenance", status=503)

        feedback_request = self.make_request("/feedback/send/")
        feedback_response = self.middleware(feedback_request)

        self.assertEqual(feedback_response.status_code, 200)
        self.get_response.assert_called_once_with(feedback_request)

        self.get_response.reset_mock()
        page_request = self.make_request("/")
        page_response = self.middleware(page_request)

        self.assertEqual(page_response.status_code, 503)
        render.assert_called_once_with(
            page_request,
            "default/errors/maintenance.html",
            status=503,
            context={"seo": get_default_seo.return_value},
        )
