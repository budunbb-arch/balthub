from django.test import SimpleTestCase

from apps.core.engines.context_processors import _route_matches


class ModuleRouteMatchingTests(SimpleTestCase):
    def test_route_prefix_matches_account_urls(self):
        self.assertTrue(_route_matches("account", "account_dashboard", "/account/"))
        self.assertTrue(
            _route_matches("account", "account_login", "/account/login/")
        )

    def test_route_prefix_does_not_match_similarly_named_url(self):
        self.assertFalse(
            _route_matches("account", "other", "/accounting/")
        )

    def test_exact_view_name_remains_supported(self):
        self.assertTrue(
            _route_matches("account_dashboard", "account_dashboard", "/account/")
        )

    def test_empty_route_is_global(self):
        self.assertTrue(_route_matches("", "home", "/"))
