from apps.core.common.querysets import PublicQuerySet


class HouseQuerySet(PublicQuerySet):

    def active(self):
        return self.public().filter(
            project__is_deleted=False,
            project__is_public=True,

            project__developer__is_deleted=False,
            project__developer__is_public=True,
        )

    def deadline_years(self, years):

        if not years:
            return self

        return self.filter(
            params__deadline_year__in=years
        )

    def building_statuses(self, statuses):

        if not statuses:
            return self

        return self.filter(
            params__building_status_id__in=statuses
        )

    def phases(self, phases):

        if not phases:
            return self

        return self.filter(
            params__phase__in=phases
        )

    def for_project(self, project):

        if not project:
            return self

        return self.filter(
            project=project
        )

    def for_developer(self, developer):

        if not developer:
            return self

        return self.filter(
            project__developer=developer
        )

    def sorted(self, value):

        allowed = {

            "-id": "-id",
            "id": "id",

            "deadline_year": "params__deadline_year",
            "-deadline_year": "-params__deadline_year",

            "floors": "params__floors",
            "-floors": "-params__floors",
        }

        return self.order_by(
            allowed.get(value, "-id"),
            "id"
        )

    def available_deadline_years(self):

        return (
            self
            .exclude(params__deadline_year__isnull=True)
            .values_list(
                "params__deadline_year",
                flat=True
            )
            .distinct()
            .order_by("params__deadline_year")
        )


    def available_phases(self):

        return (
            self
            .exclude(params__phase__isnull=True)
            .exclude(params__phase__exact="")
            .values_list(
                "params__phase",
                flat=True
            )
            .distinct()
            .order_by("params__phase")
        )  