from apps.estates.houses.models import House


class MapEngine:

    @staticmethod
    def houses_queryset(qs):
        """
        Превращает queryset домов в список точек карты.
        """

        points = []

        for house in (
            qs.select_related("project", "params")
              .select_related(
                  "project__project_type",
                  "project__params__city",
              )
              .filter(
                  params__latitude__isnull=False,
                  params__longitude__isnull=False,
              )
        ):

            points.append({
                "id": house.id,
                "title": house.params.address or str(house),
                "lat": house.params.latitude,
                "lon": house.params.longitude,
                "url": house.get_absolute_url(),
                "project": house.project.name,
                "project_type_alias": (
                    house.project.project_type.project_type_alias
                    if house.project.project_type
                    else ""
                ),
                "city": (
                    house.project.params.city.name
                    if hasattr(house.project, "params")
                    and house.project.params.city
                    else ""
                ),
                "corpus": house.params.corpus or "",
                "address": house.params.address or "",
            })

        return points

    @staticmethod
    def all_houses():

        qs = House.objects.active()

        return MapEngine.houses_queryset(qs)

    @staticmethod
    def project_houses(project):

        qs = House.objects.active().filter(project=project)

        return MapEngine.houses_queryset(qs)

    @staticmethod
    def one_house(house):

        if not (
            house.params.latitude
            and
            house.params.longitude
        ):
            return []

        return [{
            "id": house.id,
            "title": house.params.address or str(house),
            "lat": house.params.latitude,
            "lon": house.params.longitude,
            "url": house.get_absolute_url(),
            "project": house.project.name,
        }]