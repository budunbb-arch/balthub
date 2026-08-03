from types import SimpleNamespace

from django.test import SimpleTestCase

from apps.estates.parsing.services.nmarket.helpers import should_skip_parser_update


class ParserUpdateGuardTests(SimpleTestCase):
    def test_skips_objects_with_edited_at(self):
        instance = SimpleNamespace(pk=1, edited_at="2024-01-01T00:00:00Z", edited_by=None)

        self.assertTrue(should_skip_parser_update(instance))

    def test_skips_objects_with_edited_by(self):
        instance = SimpleNamespace(pk=1, edited_at=None, edited_by=SimpleNamespace(pk=2))

        self.assertTrue(should_skip_parser_update(instance))

    def test_allows_parser_updates_for_unedited_objects(self):
        instance = SimpleNamespace(pk=1, edited_at=None, edited_by=None)

        self.assertFalse(should_skip_parser_update(instance))
