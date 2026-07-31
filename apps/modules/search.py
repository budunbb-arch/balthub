# /opt/balthub/apps/modules/search.py

from apps.core.dictionaries.models import City, District, PropertyType
from apps.estates.flats.models import FlatParams


MODULE = "default/modules/search.html"


PRICE_BANDS = [
    (0, 2_000_000, "до 2 млн"),
    (2_000_000, 4_000_000, "2–4 млн"),
    (4_000_000, 6_000_000, "4–6 млн"),
    (6_000_000, 10_000_000, "6–10 млн"),
    (10_000_000, None, "от 10 млн"),
]


def get_context(request, module):

    return {
        "cities": City.objects.all(),
        "districts": District.objects.all(),
        "property_types": PropertyType.objects.all(),
        "rooms_aliases": FlatParams.objects.exclude(
            rooms_alias__isnull=True
        ).exclude(
            rooms_alias__exact=""
        ).values_list(
            "rooms_alias", flat=True
        ).distinct().order_by("rooms_alias"),
        "price_bands": PRICE_BANDS,
    }
