# /opt/balthub/apps/estates/flats/views.py

from django.shortcuts import render, get_object_or_404
from apps.estates.flats.models import Flat
from apps.maps.engine import MapEngine


def flat_detail(request, project_slug, house_slug, flat_slug):
    flat = get_object_or_404(
        Flat.objects.active().select_related(
            "house",
            "house__project",
            "params",
        ).prefetch_related(
            "deals__currency",
            "deals__deal_type",
            "flat_tags__tag",
        ),
        slug=flat_slug,
        house__slug=house_slug,
        house__project__slug=project_slug,
    )

    try:
        map_points = MapEngine.one_house(flat.house)
    except Exception:
        map_points = []

    context = {
        "flat": flat,
        "map_points": map_points,
    }

    return render(request, "default/pages/estates/flat_detail.html", context)
