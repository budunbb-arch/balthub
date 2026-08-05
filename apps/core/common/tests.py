from django.test import SimpleTestCase

from apps.core.common.admin import RelativeURLField
from apps.estates.projects.admin import ProjectImageInline
from apps.estates.projects.models import ProjectImage


class RelativeURLFieldTests(SimpleTestCase):
    def test_accepts_relative_media_path(self):
        field = RelativeURLField()

        value = field.clean("/media/images/house.jpg")

        self.assertEqual(value, "/media/images/house.jpg")

    def test_accepts_absolute_url(self):
        field = RelativeURLField()

        value = field.clean("https://example.com/media/images/house.jpg")

        self.assertEqual(value, "https://example.com/media/images/house.jpg")

    def test_rejects_invalid_value(self):
        field = RelativeURLField()

        with self.assertRaises(Exception):
            field.clean("not a valid url")

    def test_inline_uses_relative_url_field(self):
        field = ProjectImageInline.formfield_for_dbfield(
            ProjectImage._meta.get_field("image"),
            request=None,
        )

        self.assertIsInstance(field, RelativeURLField)
