# /opt/balthub/apps/modules/latest_houses.py

from django.conf import settings
from django.core.cache import cache
from apps.estates.houses.models import House


def get_latest_houses(request):

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

    cache_key = "latest_houses"

    houses = cache.get(cache_key)

    if houses is None:

        houses = list(

            House.objects

            .select_related(
                "project",
                "project__params__city",
                "params",
                "params__house_structure_type",
                "params__building_status",
            )

            .order_by("-id")[:8]
        )

        cache.set(
            cache_key,
            houses,
            settings.CACHE_TTL
        )

    return {
        "latest_houses": houses
    }