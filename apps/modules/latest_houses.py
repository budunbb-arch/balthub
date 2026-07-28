# /opt/balthub/apps/modules/latest_houses.py

from apps.estates.houses.models import House


# apps/modules/latest_houses.py

MODULE = "default/modules/latest_houses.html"


def get_context(request, module):

    resolver_match = getattr(
        request,
        "resolver_match",
        None
    )

    view_name = getattr(
        resolver_match,
        "view_name",
        None
    )

    if view_name != "home":
        return {}

    houses = list(

        House.objects
        .active()
        .select_related(
            "project",
            "project__params__city",
            "params",
            "params__house_structure_type",
            "params__building_status",
        )

        .order_by("-id")[:8]
    )

    return {
        "latest_houses": houses
    }