# /opt/balthub/apps/estates/houses/views.py

from django.db.models import Min, Max, Count, F, FloatField, ExpressionWrapper
from django.db.models.functions import Round
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.urls import reverse

from apps.estates.houses.models import House
from apps.estates.projects.models import Project
from apps.estates.flats.models import Flat, FlatParams
from apps.maps.models import MapSettings
from apps.maps.engine import MapEngine

from apps.core.dictionaries.models import (
    BalconyType,
    BathroomUnitType,
    FinishType,
)

from apps.core.pagination import paginate_queryset, build_page_range
from apps.core.engines.picker import normalize_querydict
from .pickers import house_list_pickers, house_detail_pickers

import json


def house_list(request):

    state = normalize_querydict(request)

    selected_deadlines = state.get("deadline_year", [])
    selected_statuses = state.get("building_status", [])
    selected_phases = state.get("phase", [])

    sort = state.get("sort", ["-id"])[0]

    # =====================================================
    # QUERYSET
    # =====================================================

    qs = (

        House.objects

        .active()

        .deadline_years(selected_deadlines)

        .building_statuses(selected_statuses)

        .phases(selected_phases)

        .select_related(
            "project",
            "project__developer",
            "project__params__city",
            "params",
            "params__house_structure_type",
            "params__building_status",
        )

        .sorted(sort)
    )

    # =====================================================
    # PAGINATION
    # =====================================================

    page_obj, paginator, page_range = paginate_queryset(
        request,
        qs,
        12
    )

    pickers = house_list_pickers(

        sort=sort,

        selected_deadlines=selected_deadlines,
        selected_statuses=selected_statuses,
        selected_phases=selected_phases,
    )

    context = {
        "page_obj": page_obj,
        "paginator": paginator,
        "page_range": page_range,
        "pickers": pickers,
    }

    # =====================================================
    # AJAX
    # =====================================================

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":

        return render(
            request,
            "default/pages/estates/ajax/_house_list.html",
            context
        )

    return render(
        request,
        "default/pages/estates/house_list.html",
        context
    )


def house_detail(request, project_slug, house_slug):

    project = get_object_or_404(
        Project.objects.only("id", "slug"),
        slug=project_slug
    )

    house = get_object_or_404(

        House.objects.active().select_related(
            "project",
            "project__params__city",
            "params",
        ),

        slug=house_slug,
        project=project
    )

    request.house = house

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

    qs = (

        Flat.objects.active().for_house(house)

        .select_related(
            "params"
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
        .for_house(house)
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

    rooms_groups = (
        Flat.objects.active().for_house(house).available_rooms()
    )

    rooms_alias_queryset = (
        FlatParams.objects
        .filter(flat__house=house)
        .exclude(rooms_alias__isnull=True)
        .exclude(rooms_alias__exact="")
        .values_list("rooms_alias", flat=True)
        .distinct()
        .order_by("rooms")
    )

    balcony_type_ids = (
        FlatParams.objects
        .filter(flat__house=house)
        .exclude(balcony_type__isnull=True)
        .values_list("balcony_type", flat=True)
        .distinct()
    )
    balcony_type_queryset = BalconyType.objects.filter(id__in=balcony_type_ids).order_by("-name")

    bathroom_unit_type_ids = (
        FlatParams.objects
        .filter(flat__house=house)
        .exclude(bathroom_unit_type__isnull=True)
        .values_list("bathroom_unit_type", flat=True)
        .distinct()
    )
    bathroom_unit_type_queryset = BathroomUnitType.objects.filter(id__in=bathroom_unit_type_ids).order_by("name")

    finish_type_ids = (
        FlatParams.objects
        .filter(flat__house=house)
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

    settings = MapSettings.get_solo()

    context = {
        "house": house,

        "page_obj": page_obj,
        "paginator": paginator,
        "page_range": page_range,

        "pickers": pickers,
        "rooms_groups": rooms_groups,

        "pagination_template": "default/includes/minimal_pagination.html",

        "YANDEX_API_KEY": settings.api_key if settings.provider == MapSettings.PROVIDER_YANDEX else "",

        "flats_page_obj": page_obj,
        "flats_paginator": paginator,
        "flats_page_range": page_range,
        "flats_pickers": pickers,
    }

    context["map_points"] = MapEngine.one_house(house)

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
        "default/pages/estates/house_detail.html",
        context
    )

def flat_plans(house=None, rooms=None, page=1, per_page=6):

    qs = FlatParams.objects.filter(
        flat__in=Flat.objects.active()
    ).select_related(
        "flat__house__project__params__city",
        "flat__house__params",
        "balcony_type",
        "bathroom_unit_type",
        "finish_type",
    )

    if house is not None:
        qs = qs.filter(flat__house=house)

    if rooms is not None:

        qs = qs.filter(
            rooms=rooms
        )

    plans = (
        qs
        .annotate(
            min_price=Min("flat__deals__price"),
        )
        .annotate(
            price_per_m2=Round(
                ExpressionWrapper(
                    F("min_price") / F("square"),
                    output_field=FloatField(),
                ),
                0
            )
        )
        .annotate(
            flats_count=Count("flat_id", distinct=True),
            plan_image=Min("flat__plan"),
        )
        .order_by("square")
    )

    paginator = Paginator(
        plans,
        per_page
    )

    page_obj = paginator.get_page(page)

    return page_obj


def house_plans_ajax(request, house_slug):

    house = get_object_or_404(
        House.objects.active(),
        slug=house_slug
    )

    rooms = request.GET.get("rooms")

    if rooms in (None, "", "null"):
        rooms = None
    else:
        rooms = int(rooms)

    page = request.GET.get(
        "page",
        1
    )

    page_obj = flat_plans(
        house=house,
        rooms=rooms,
        page=page,
        per_page=6,
    )

    page_range = build_page_range(page_obj)

    return render(
        request,
        "default/pages/estates/ajax/_plans_items.html",
        {
            "page_obj": page_obj,
            "paginator": page_obj.paginator,
            "page_range": page_range,
            "house": house,
            "rooms": rooms,
            "pagination_template": "default/includes/minimal_pagination.html",
        }
    )


def plans(request):
    rooms_groups = (

        Flat.objects

        .active()

        .exclude(
            params__rooms__isnull=True
        )

        .values_list(
            "params__rooms",
            flat=True
        )

        .distinct()

        .order_by(
            "params__rooms"
        )
    )

    rooms_groups = list(rooms_groups)
    first_room = rooms_groups[0] if rooms_groups else None
    page_obj = None
    page_range = None
    paginator = None
    if first_room is not None:
        page_obj = flat_plans(house=None, rooms=first_room, page=1, per_page=6)
        page_range = build_page_range(page_obj)
        paginator = page_obj.paginator

    context = {
        "rooms_groups": rooms_groups,
        "page_obj": page_obj,
        "paginator": paginator,
        "page_range": page_range,
        "plans_url": reverse("plans_ajax"),
        "pagination_template": "default/includes/plans_pagination.html",
    }
    return render(request, "default/pages/estates/plans.html", context)


def plans_ajax(request):
    rooms = request.GET.get("rooms")
    if rooms in (None, "", "null"):
        rooms = None
    else:
        rooms = int(rooms)
    page = request.GET.get("page", 1)
    page_obj = flat_plans(house=None, rooms=rooms, page=page, per_page=6)
    page_range = build_page_range(page_obj)
    return render(
        request,
        "default/pages/estates/ajax/_plans_items.html",
        {
            "page_obj": page_obj,
            "paginator": page_obj.paginator,
            "page_range": page_range,
            "rooms": rooms,
            "plans_url": reverse("plans_ajax"),
            "pagination_template": "default/includes/plans_pagination.html",

        }
    )