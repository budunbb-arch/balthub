# apps/core/dictionaries/views.py

from django.http import JsonResponse
from apps.core.dictionaries.models import District


def districts_by_city(request):
    city_id = request.GET.get("city")

    if not city_id:
        return JsonResponse({"results": []})

    districts = (
        District.objects
        .filter(city_id=city_id)
        .values("id", "name")
        .order_by("name")
    )

    return JsonResponse({
        "results": list(districts)
    })
