# /opt/balthub/apps/estates/flats/views.py

from django.db.models import FloatField, ExpressionWrapper, F, Min, Max, Count
from django.db.models.functions import Round
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from apps.estates.flats.models import Flat, FlatParams
from apps.estates.houses.models import House
from apps.estates.projects.models import Project
from apps.maps.engine import MapEngine
from apps.core.dictionaries.models import (
    BalconyType,
    BathroomUnitType,
    FinishType,
)
from apps.core.pagination import paginate_queryset, build_page_range
from apps.core.engines.picker import normalize_querydict
from apps.estates.houses.pickers import house_detail_pickers


def flat_detail(request, project_slug, house_slug, flat_slug):
    flat = get_object_or_404(
        Flat.objects.active()
        .select_related(
            "house",
            "house__project",
            "params",
        )
        .prefetch_related(
            "deals__currency",
            "deals__deal_type",
            "flat_tags__tag",
        )
        .min_price()
        .annotate(
            price_per_m2=Round(
                ExpressionWrapper(
                    F("price") / F("params__square"),
                    output_field=FloatField(),
                ),
                0
            )
        ),
        slug=flat_slug,
        house__slug=house_slug,
        house__project__slug=project_slug,
    )

    try:
        map_points = MapEngine.one_house(flat.house)
    except Exception:
        map_points = []

    # =====================================================
    # OTHER FLATS IN PROJECT
    # =====================================================

    state = normalize_querydict(request)

    selected_rooms_alias = state.get("rooms_alias", [])
    selected_balcony_type = state.get("balcony_type", [])
    selected_bathroom_unit_type = state.get("bathroom_unit_type", [])
    selected_finish_type = state.get("finish_type", [])
    selected_haggle = state.get("haggle", [])
    selected_mortgage = state.get("mortgage", [])

    sort = state.get("sort", ["price"])[0]

    floor_from = state.get("floor_from", [""])[0]
    floor_to = state.get("floor_to", [""])[0]

    ceiling_height_from = state.get("ceiling_height_from", [""])[0]
    ceiling_height_to = state.get("ceiling_height_to", [""])[0]

    square_from = state.get("square_from", [""])[0]
    square_to = state.get("square_to", [""])[0]

    living_square_from = state.get("living_square_from", [""])[0]
    living_square_to = state.get("living_square_to", [""])[0]

    kitchen_square_from = state.get("kitchen_square_from", [""])[0]
    kitchen_square_to = state.get("kitchen_square_to", [""])[0]

    price_from = state.get("price_from", [""])[0]
    price_to = state.get("price_to", [""])[0]

    # =====================================================
    # QUERYSET
    # =====================================================

    project = flat.house.project

    qs = (
        Flat.objects.active()
        .filter(house__project=project)
        .exclude(id=flat.id)
        .select_related("params")
        .prefetch_related(
            "deals__currency",
            "deals__deal_type",
            "flat_tags__tag",
        )
        .min_price()
        .annotate(
            price_per_m2=Round(
                ExpressionWrapper(
                    F("price") / F("params__square"),
                    output_field=FloatField(),
                ),
                0
            )
        )
        .rooms_alias(selected_rooms_alias)
        .balcony_type(selected_balcony_type)
        .bathroom_unit_type(selected_bathroom_unit_type)
        .finish_type(selected_finish_type)
        .haggle(selected_haggle)
        .mortgage(selected_mortgage)
        .floor_from(floor_from)
        .floor_to(floor_to)
        .ceiling_height_from(ceiling_height_from)
        .ceiling_height_to(ceiling_height_to)
        .square_from(square_from)
        .square_to(square_to)
        .living_square_from(living_square_from)
        .living_square_to(living_square_to)
        .kitchen_square_from(kitchen_square_from)
        .kitchen_square_to(kitchen_square_to)
        .price_from(price_from)
        .price_to(price_to)
        .sorted(sort)
        .distinct()
    )

    # =====================================================
    # PAGINATION
    # =====================================================

    page_obj, paginator, page_range = paginate_queryset(
        request,
        qs,
        8
    )

    # =====================================================
    # PICKER LIMITS
    # =====================================================

    base_qs = (
        Flat.objects
        .active()
        .filter(house__project=project)
        .exclude(id=flat.id)
    )

    square_limits = base_qs.square_limits()
    price_limits = qs.price_limits()
    floor_limits = base_qs.floor_limits()
    ceiling_height_limits = base_qs.ceiling_height_limits()
    living_square_limits = base_qs.living_square_limits()
    kitchen_square_limits = base_qs.kitchen_square_limits()

    # =====================================================
    # PICKER OPTIONS
    # =====================================================

    rooms_alias_queryset = (
        FlatParams.objects
        .filter(flat__house__project=project)
        .exclude(flat_id=flat.id)
        .exclude(rooms_alias__isnull=True)
        .exclude(rooms_alias__exact="")
        .values_list("rooms_alias", flat=True)
        .distinct()
        .order_by("rooms")
    )

    balcony_type_ids = (
        FlatParams.objects
        .filter(flat__house__project=project)
        .exclude(flat_id=flat.id)
        .exclude(balcony_type__isnull=True)
        .values_list("balcony_type", flat=True)
        .distinct()
    )
    balcony_type_queryset = BalconyType.objects.filter(id__in=balcony_type_ids).order_by("-name")

    bathroom_unit_type_ids = (
        FlatParams.objects
        .filter(flat__house__project=project)
        .exclude(flat_id=flat.id)
        .exclude(bathroom_unit_type__isnull=True)
        .values_list("bathroom_unit_type", flat=True)
        .distinct()
    )
    bathroom_unit_type_queryset = BathroomUnitType.objects.filter(id__in=bathroom_unit_type_ids).order_by("name")

    finish_type_ids = (
        FlatParams.objects
        .filter(flat__house__project=project)
        .exclude(flat_id=flat.id)
        .exclude(finish_type__isnull=True)
        .values_list("finish_type", flat=True)
        .distinct()
    )
    finish_type_queryset = FinishType.objects.filter(id__in=finish_type_ids).order_by("name")

    # =====================================================
    # PICKERS
    # =====================================================

    pickers = house_detail_pickers(
        sort=sort,
        selected_rooms_alias=selected_rooms_alias,
        selected_floor_from=floor_from,
        selected_floor_to=floor_to,
        selected_ceiling_height_from=ceiling_height_from,
        selected_ceiling_height_to=ceiling_height_to,
        selected_square_from=square_from,
        selected_square_to=square_to,
        selected_living_square_from=living_square_from,
        selected_living_square_to=living_square_to,
        selected_kitchen_square_from=kitchen_square_from,
        selected_kitchen_square_to=kitchen_square_to,
        selected_balcony_type=selected_balcony_type,
        selected_bathroom_unit_type=selected_bathroom_unit_type,
        selected_finish_type=selected_finish_type,
        selected_haggle=selected_haggle,
        selected_mortgage=selected_mortgage,
        price_limits=price_limits,
        rooms_alias_queryset=rooms_alias_queryset,
        balcony_type_queryset=balcony_type_queryset,
        bathroom_unit_type_queryset=bathroom_unit_type_queryset,
        finish_type_queryset=finish_type_queryset,
        floor_limits=floor_limits,
        ceiling_height_limits=ceiling_height_limits,
        square_limits=square_limits,
        living_square_limits=living_square_limits,
        kitchen_square_limits=kitchen_square_limits,
    )

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {
        "flat": flat,
        "map_points": map_points,
        "project": project,
        "flats_page_obj": page_obj,
        "flats_paginator": paginator,
        "flats_page_range": page_range,
        "flats_pickers": pickers,
    }

    request.flat = flat

    # =====================================================
    # AJAX
    # =====================================================

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render(
            request,
            "default/pages/estates/ajax/_flat_list.html",
            context
        )

    return render(
        request,
        "default/pages/estates/flat_detail.html",
        context
    )
