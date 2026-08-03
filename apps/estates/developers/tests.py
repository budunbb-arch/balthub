from django.contrib.admin.sites import site
from django.test import TestCase

from apps.estates.developers.admin import DeveloperAdmin, DeveloperDescriptionInline
from apps.estates.developers.models import Developer, DeveloperDescription


class DeveloperAdminTests(TestCase):
    def test_description_inline_is_available_in_developer_admin(self):
        admin_instance = DeveloperAdmin(Developer, site)

        self.assertIn(DeveloperDescriptionInline, admin_instance.inlines)
        self.assertTrue(issubclass(DeveloperDescriptionInline.model, DeveloperDescription))
