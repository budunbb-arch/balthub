from django.db.models import Count, Min, Q, Prefetch

from apps.core.common.querysets import PublicQuerySet


class ProjectQuerySet(PublicQuerySet):

    def active(self):
        return self.public().filter(
            developer__is_deleted=False,
            developer__is_public=True,
        )

    def with_flat_stats(self):
        return self.annotate(
            flats_count=Count(
                "houses__flats",
                filter=Q(
                    houses__flats__is_public=True,
                    houses__flats__is_deleted=False,
                ),
                distinct=True,
            ),
            min_price=Min(
                "houses__flats__deals__price",
                filter=Q(
                    houses__flats__is_public=True,
                    houses__flats__is_deleted=False,
                ),
            ),
        )

    def for_developer(self, developer):

        if not developer:
            return self

        return self.filter(
            developer=developer
        )

    def cities(self, cities):

        if not cities:
            return self

        return self.filter(
            params__city_id__in=cities
        )

    def districts(self, districts):

        if not districts:
            return self

        return self.filter(
            params__district_id__in=districts
        )

    def property_categories(self, categories):

        if not categories:
            return self

        return self.filter(
            params__property_category_id__in=categories
        )

    def city(self, cities):

        if not cities:
            return self

        return self.filter(
            params__city_id__in=cities
        )

    def district(self, districts):

        if not districts:
            return self

        return self.filter(
            params__district_id__in=districts
        )

    def developer(self, developers):

        if not developers:
            return self

        return self.filter(
            developer_id__in=developers
        )

    def property_category(self, categories):

        if not categories:
            return self

        return self.filter(
            params__property_category_id__in=categories
        )

    def sorted(self, value):

        allowed = {
            "name": "name",
            "-name": "-name",

            "city": "params__city__name",
            "-city": "-params__city__name",
        }

        return self.order_by(
            allowed.get(value, "name"),
            "id"
        )