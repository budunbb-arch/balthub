# /opt/balthub/apps/estates/flats/views.py

from django.shortcuts import render, get_object_or_404
from apps.estates.flats.models import Flat


def flat_detail(request, project_slug, house_slug, flat_slug):
    flat = get_object_or_404(
        Flat.objects.active().select_related(
            "house",
            "house__project",
            "params",
        ).prefetch_related(
            "deals__currency",
            "deals__deal_type",
        ),
        slug=flat_slug,
        house__slug=house_slug,
        house__project__slug=project_slug,
    )

    return render(request, "default/pages/estates/flat_detail.html", {
        "flat": flat
    })
