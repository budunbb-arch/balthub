from django.test import TestCase

from apps.core.dictionaries.models import ProjectType
from apps.estates.parsing.cache import ImportCache


class ProjectTypeResolutionTests(TestCase):
    def setUp(self):
        self.default_type = ProjectType.objects.create(
            name="Жилой дом",
            default=True,
        )
        self.apartment_hotel_type = ProjectType.objects.create(
            name="Апарт-отель",
            project_type_alias="апарт гостиница",
        )
        self.cache = ImportCache()
        self.cache.load_project_types()

    def test_resolves_name_case_insensitively_and_removes_type(self):
        name, project_type = self.cache.resolve_project_type(
            "АПАРТ-ОТЕЛЬ Пионерский"
        )

        self.assertEqual(name, "Пионерский")
        self.assertEqual(project_type, self.apartment_hotel_type)

    def test_resolves_alias_case_insensitively(self):
        name, project_type = self.cache.resolve_project_type(
            "АпАРт гостиница Светлогорск"
        )

        self.assertEqual(name, "Светлогорск")
        self.assertEqual(project_type, self.apartment_hotel_type)

    def test_uses_default_type_when_no_type_matches(self):
        name, project_type = self.cache.resolve_project_type("Пионерский")

        self.assertEqual(name, "Пионерский")
        self.assertEqual(project_type, self.default_type)

    def test_matches_longest_type_phrase(self):
        long_type = ProjectType.objects.create(name="Жилой дом у моря")
        self.cache.load_project_types()

        name, project_type = self.cache.resolve_project_type(
            "Жилой дом у моря Пионерский"
        )

        self.assertEqual(name, "Пионерский")
        self.assertEqual(project_type, long_type)

    def test_does_not_match_type_inside_another_word(self):
        name, project_type = self.cache.resolve_project_type("Домик у озера")

        self.assertEqual(name, "Домик у озера")
        self.assertEqual(project_type, self.default_type)

    def test_raises_for_equally_specific_types(self):
        ProjectType.objects.create(
            name="Гостиница",
            project_type_alias="апарт-отель",
        )
        self.cache.load_project_types()

        with self.assertRaisesRegex(RuntimeError, "Неоднозначный тип"):
            self.cache.resolve_project_type("Апарт-отель Пионерский")
