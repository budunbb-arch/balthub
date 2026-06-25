# /opt/balthub/apps/estates/developers/queries.py

from django.db.models import Min, Max, Count, Q, Prefetch
from apps.core.common.querysets import PublicQuerySet


class DeveloperQuerySet(PublicQuerySet):

    def active(self):
        return self.public()

    def with_detail_stats(self):

        return self.annotate(

            projects_count=Count(
                "projects",
                filter=Q(
                    projects__is_public=True,
                    projects__is_deleted=False,
                ),
                distinct=True
            ),

            houses_count=Count(
                "projects__houses",
                filter=Q(
                    projects__houses__is_public=True,
                    projects__houses__is_deleted=False,
                ),
                distinct=True
            ),

            flats_count=Count(
                "projects__houses__flats",
                filter=Q(
                    projects__houses__flats__is_public=True,
                    projects__houses__flats__is_deleted=False,
                ),
                distinct=True
            ),

            min_price=Min(
                "projects__houses__flats__deals__price"
            ),

            max_price=Max(
                "projects__houses__flats__deals__price"
            ),
        )

    def with_contacts(self):

        from apps.estates.developers.models import (
            DeveloperContact,
        )

        return self.prefetch_related(
            Prefetch(
                "developercontacts",
                queryset=DeveloperContact.objects.select_related(
                    "contact_type"
                )
            )
        )

    def with_departments(self):

        from apps.estates.developers.models import (
            DeveloperDepartment,
            DepartmentContact,
        )

        return self.prefetch_related(
            Prefetch(
                "developerdepartments",
                queryset=DeveloperDepartment.objects.prefetch_related(
                    Prefetch(
                        "contacts",
                        queryset=DepartmentContact.objects.select_related(
                            "contact_type"
                        )
                    )
                )
            )
        )

    def cities(self, cities):

        if not cities:
            return self

        return self.filter(
            projects__params__city_id__in=cities
        )

    def property_categories(self, categories):

        if not categories:
            return self

        return self.filter(
            projects__params__property_category_id__in=categories
        )

    def min_price_from(self, value):

        if not value:
            return self

        return self.filter(
            min_price__gte=value
        )

    def min_price_to(self, value):

        if not value:
            return self

        return self.filter(
            min_price__lte=value
        )

    def with_list_stats(self):

        return self.annotate(
            projects_count=Count(
                "projects",
                distinct=True
            ),

            min_price=Min(
                "projects__houses__flats__deals__price"
            ),
        )

    def sorted(self, value):

        allowed = {

            "name": "name",
            "-name": "-name",

            "projects": "projects_count",
            "-projects": "-projects_count",

            "price": "min_price",
            "-price": "-min_price",
        }

        return self.order_by(
            allowed.get(value, "name"),
            "id"
        )

    def price_limits(self):

        return self.aggregate(
            min_price=Min(
                "projects__houses__flats__deals__price"
            ),
            max_price=Max(
                "projects__houses__flats__deals__price"
            ),
        )

    def detail(self):

        return (
            self
            .with_detail_stats()
            .with_contacts()
            .with_departments()
            .prefetch_related("developerdescriptions")
        )