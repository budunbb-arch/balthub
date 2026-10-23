from unittest.mock import patch

from django.test import RequestFactory, TestCase
from django.urls import reverse

from apps.core.dictionaries.models import City, District, ProjectType
from apps.estates.developers.models import Developer
from apps.estates.houses.models import House, HouseParams
from apps.estates.projects.models import Project, ProjectParams
from apps.estates.projects.views import geography_detail, geography_list


class GeographyViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.city = City.objects.create(name="Калининград")
        project_type = ProjectType.objects.create(
            name="Жилой комплекс",
            project_type_alias="ЖК",
        )
        self.developer = Developer.objects.create(
            name="Застройщик",
            is_public=True,
        )
        self.project = Project.objects.create(
            name="Тестовый проект",
            external_id="geography-test-project",
            developer=self.developer,
            project_type=project_type,
            is_public=True,
        )
        ProjectParams.objects.create(project=self.project, city=self.city)

    def test_city_slug_is_generated_for_geography_url(self):
        self.assertEqual(self.city.slug, "kaliningrad")
        self.assertEqual(
            reverse("geography_detail", kwargs={"city_slug": self.city.slug}),
            "/estates/geography/kaliningrad/",
        )

    def test_geography_list_contains_only_cities_with_active_projects(self):
        request = self.factory.get(reverse("geography_list"))

        with patch("apps.estates.projects.views.render") as render:
            geography_list(request)

        context = render.call_args.args[2]
        self.assertTrue(context["is_geo"])
        self.assertEqual(list(context["cities"]), [self.city])

    def test_geography_list_passes_each_active_house_as_a_map_marker(self):
        houses = [
            House.objects.create(
                project=self.project,
                external_id=f"geography-test-house-{number}",
                is_public=True,
            )
            for number in (1, 2)
        ]
        HouseParams.objects.bulk_create([
            HouseParams(
                house=house,
                latitude=54.70 + number / 100,
                longitude=20.50 + number / 100,
                address=f"Дом {number}",
                corpus=f"Корпус {number}",
            )
            for number, house in enumerate(houses, start=1)
        ])
        request = self.factory.get(reverse("geography_list"))

        with patch("apps.estates.projects.views.render") as render:
            geography_list(request)

        map_points = render.call_args.args[2]["map_points"]
        self.assertEqual(len(map_points), 2)
        self.assertEqual(
            {(point["lat"], point["lon"]) for point in map_points},
            {(54.71, 20.51), (54.72, 20.52)},
        )
        self.assertEqual(map_points[0]["city"], self.city.name)
        self.assertEqual(map_points[0]["project"], self.project.name)
        self.assertEqual(map_points[0]["project_type_alias"], "ЖК")
        self.assertEqual(map_points[0]["corpus"], "Корпус 1")

    def test_geography_detail_contains_city_projects(self):
        district = District.objects.create(city=self.city, name="Центральный")
        self.project.params.district = district
        self.project.params.save()
        request = self.factory.get(
            reverse("geography_detail", kwargs={"city_slug": self.city.slug})
        )

        with patch("apps.estates.projects.views.render") as render:
            geography_detail(request, self.city.slug)

        context = render.call_args.args[2]
        self.assertTrue(context["is_geo"])
        self.assertEqual(context["city"], self.city)
        self.assertEqual(list(context["page_obj"].object_list), [self.project])
        self.assertEqual(request.geo_city, self.city)
        city_picker, district_picker = context["pickers"][1:3]
        self.assertEqual(city_picker["value"], [str(self.city.pk)])
        self.assertEqual(
            [option["value"] for option in city_picker["options"]],
            [str(self.city.pk)],
        )
        self.assertFalse(district_picker["disabled"])
        self.assertEqual(
            [option["value"] for option in district_picker["options"]],
            [str(district.pk)],
        )

    def test_geography_detail_filters_projects_by_district_and_developer(self):
        district = District.objects.create(city=self.city, name="Центральный")
        self.project.params.district = district
        self.project.params.save()
        request = self.factory.get(
            reverse("geography_detail", kwargs={"city_slug": self.city.slug}),
            {
                "district": str(district.pk),
                "developer": str(self.developer.pk),
                "sort": "-name",
            },
        )

        with patch("apps.estates.projects.views.render") as render:
            geography_detail(request, self.city.slug)

        context = render.call_args.args[2]
        self.assertEqual(list(context["page_obj"].object_list), [self.project])
        self.assertEqual(context["pickers"][0]["value"], "-name")
        self.assertEqual(context["pickers"][2]["value"], [str(district.pk)])
        self.assertEqual(context["pickers"][3]["value"], [str(self.developer.pk)])

    def test_geography_detail_returns_ajax_partial_for_load_more(self):
        request = self.factory.get(
            reverse("geography_detail", kwargs={"city_slug": self.city.slug}),
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        with patch("apps.estates.projects.views.render") as render:
            geography_detail(request, self.city.slug)

        self.assertEqual(
            render.call_args.args[1],
            "default/pages/estates/ajax/_geography_projects.html",
        )
