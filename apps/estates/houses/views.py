# /opt/balthub/apps/estates/houses/views.py

from django.db.models import Q, Min, Max, Count, F, FloatField, ExpressionWrapper
from django.db.models.functions import Round
from django.shortcuts import render, get_object_or_404
from django.core.cache import cache
from django.core.paginator import Paginator
from django.conf import settings
from django.urls import reverse

from collections import defaultdict

from apps.estates.houses.models import House
from apps.estates.projects.models import Project
from apps.estates.developers.models import Developer
from apps.estates.flats.models import Flat, FlatParams

from apps.core.dictionaries.models import BuildingStatus

from apps.core.cache_keys import (
    house_list_key,
    project_detail_key,
)

from apps.core.pagination import paginate_queryset, build_page_range
from apps.core.engines.picker import normalize_querydict


def house_list(request):

    state = normalize_querydict(request)

    selected_deadlines = state.get("deadline_year", [])
    selected_statuses = state.get("building_status", [])
    selected_phases = state.get("phase", [])

    sort = state.get("sort", ["-id"])[0]

    # =====================================================
    # SORT
    # =====================================================

    allowed_sort = {

        # новизна
        "-id": "-id",
        "id": "id",

        # срок сдачи
        "deadline_year": "params__deadline_year",
        "-deadline_year": "-params__deadline_year",

        # этажность
        "floors": "params__floors",
        "-floors": "-params__floors",
    }

    order_by = allowed_sort.get(sort, "-id")

    # =====================================================
    # QUERYSET
    # =====================================================

    qs = (

        House.objects

        .select_related(
            "project",
            "project__developer",
            "project__params__city",

            "params",
            "params__house_structure_type",
            "params__building_status",
        )

        .filter(
            is_deleted=False,
        )
    )

    filters = Q()

    # =====================================================
    # DEADLINE
    # =====================================================

    if selected_deadlines:

        filters &= Q(
            params__deadline_year__in=selected_deadlines
        )

    # =====================================================
    # BUILDING STATUS
    # =====================================================

    if selected_statuses:

        filters &= Q(
            params__building_status_id__in=selected_statuses
        )

    # =====================================================
    # PHASE
    # =====================================================

    if selected_phases:

        filters &= Q(
            params__phase__in=selected_phases
        )

    qs = qs.filter(filters)

    qs = qs.order_by(order_by, "id")

    # =====================================================
    # PAGINATION
    # =====================================================

    page_obj, paginator, page_range = paginate_queryset(
        request,
        qs,
        12
    )

    # =====================================================
    # PICKERS
    # =====================================================

    deadline_queryset = (
        House.objects
        .exclude(params__deadline_year__isnull=True)
        .values_list("params__deadline_year", flat=True)
        .distinct()
        .order_by("params__deadline_year")
    )

    phase_queryset = (
        House.objects
        .exclude(params__phase__isnull=True)
        .exclude(params__phase__exact="")
        .values_list("params__phase", flat=True)
        .distinct()
        .order_by("params__phase")
    )

    pickers = [

        # =====================================================
        # SORT
        # =====================================================

        {
            "name": "sort",
            "placeholder": "Сортировка",
            "auto_submit": True,
            "input_type": "radio",

            "options": [

                {
                    "value": "-id",
                    "label": "Сначала новые",
                },

                {
                    "value": "id",
                    "label": "Сначала старые",
                },

                {
                    "value": "deadline_year",
                    "label": "Срок сдачи ↑",
                },

                {
                    "value": "-deadline_year",
                    "label": "Срок сдачи ↓",
                },

                {
                    "value": "floors",
                    "label": "Этажность ↑",
                },

                {
                    "value": "-floors",
                    "label": "Этажность ↓",
                },
            ]
        },

        # =====================================================
        # DEADLINE YEAR
        # =====================================================

        {
            "name": "deadline_year",
            "placeholder": "Срок сдачи",
            "auto_submit": False,
            "multiple": True,
            "input_type": "checkbox",

            "options": [

                {
                    "value": str(year),
                    "label": str(year),
                }

                for year in deadline_queryset
            ]
        },

        # =====================================================
        # BUILDING STATUS
        # =====================================================

        {
            "name": "building_status",
            "placeholder": "Статус",
            "auto_submit": False,
            "multiple": True,
            "input_type": "checkbox",

            "options": [

                {
                    "value": str(status.id),
                    "label": status.name,
                }

                for status in BuildingStatus.objects.order_by("name")
            ]
        },

        # =====================================================
        # PHASE
        # =====================================================

        {
            "name": "phase",
            "placeholder": "Очередь",
            "auto_submit": False,
            "multiple": True,
            "input_type": "checkbox",

            "options": [

                {
                    "value": str(phase),
                    "label": str(phase),
                }

                for phase in phase_queryset
            ]
        },
    ]

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

        House.objects.select_related(
            "project",
            "project__params__city",
            "params",
        ),

        slug=house_slug,
        project=project
    )

    state = normalize_querydict(request)

    selected_rooms = state.get("rooms", [])

    sort = state.get("sort", ["price"])[0]

    square_from = state.get("square_from", [""])[0]
    square_to = state.get("square_to", [""])[0]

    price_from = state.get("price_from", [""])[0]
    price_to = state.get("price_to", [""])[0]

    # =====================================================
    # SORT
    # =====================================================

    allowed_sort = {

        # комнаты
        "rooms": "params__rooms",
        "-rooms": "-params__rooms",

        # площадь
        "square": "params__square",
        "-square": "-params__square",

        # цена
        "price": "price",
        "-price": "-price",
    }

    order_by = allowed_sort.get(sort, "price")

    # =====================================================
    # QUERYSET
    # =====================================================

    qs = (

        house.flats

        .select_related(
            "params"
        )

        .prefetch_related(
            "deals__currency",
            "deals__deal_type"
        )

        .annotate(
            price=Min("deals__price")
        )
    )

    filters = Q()

    # =====================================================
    # ROOMS
    # =====================================================

    if selected_rooms:

        filters &= Q(
            params__rooms__in=selected_rooms
        )

    # =====================================================
    # SQUARE
    # =====================================================

    if square_from:

        filters &= Q(
            params__square__gte=square_from
        )

    if square_to:

        filters &= Q(
            params__square__lte=square_to
        )

    # =====================================================
    # PRICE
    # =====================================================

    if price_from:

        filters &= Q(
            price__gte=price_from
        )

    if price_to:

        filters &= Q(
            price__lte=price_to
        )

    qs = qs.filter(filters)

    qs = qs.order_by(order_by, "id").distinct()

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

    limits = (

        house.flats

        .annotate(
            price=Min("deals__price")
        )

        .aggregate(

            min_square=Min("params__square"),
            max_square=Max("params__square"),

            min_price=Min("price"),
            max_price=Max("price"),
        )
    )

    # =====================================================
    # ROOMS QUERYSET
    # =====================================================

    rooms_queryset = (

        house.flats

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

    # =====================================================
    # PICKERS
    # =====================================================

    pickers = [

        # =====================================================
        # SORT
        # =====================================================

        {
            "name": "sort",
            "placeholder": "Сортировка",
            "auto_submit": True,
            "input_type": "radio",

            "options": [

                {
                    "value": "rooms",
                    "label": "Комнат ↑",
                },

                {
                    "value": "-rooms",
                    "label": "Комнат ↓",
                },

                {
                    "value": "square",
                    "label": "Площадь ↑",
                },

                {
                    "value": "-square",
                    "label": "Площадь ↓",
                },

                {
                    "value": "price",
                    "label": "Цена ↑",
                },

                {
                    "value": "-price",
                    "label": "Цена ↓",
                },
            ]
        },

        # =====================================================
        # ROOMS
        # =====================================================

        {
            "name": "rooms",
            "placeholder": "Комнаты",
            "auto_submit": False,
            "multiple": True,
            "input_type": "checkbox",

            "options": [

                {
                    "value": str(room),
                    "label": f"{room} комн.",
                }

                for room in rooms_queryset
            ]
        },

        # =====================================================
        # SQUARE RANGE
        # =====================================================

        {
            "name": "square",
            "label": "Площадь",
            "placeholder": "Площадь",
            "type": "range",
            "auto_submit": True,

            "range": {

                "from_name": "square_from",
                "to_name": "square_to",

                "from_value": square_from,
                "to_value": square_to,

                "from_placeholder": int(limits["min_square"] or 0),
                "to_placeholder": int(limits["max_square"] or 0),
            }
        },

        # =====================================================
        # PRICE RANGE
        # =====================================================

        {
            "name": "price",
            "label": "Цена",
            "placeholder": "Цена",
            "type": "range",
            "auto_submit": True,

            "range": {

                "from_name": "price_from",
                "to_name": "price_to",

                "from_value": price_from,
                "to_value": price_to,

                "from_placeholder": int(limits["min_price"] or 0),
                "to_placeholder": int(limits["max_price"] or 0),
            }
        },
    ]

    rooms_groups = (

        house.flats

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

    context = {
        "house": house,

        "page_obj": page_obj,
        "paginator": paginator,
        "page_range": page_range,

        "pickers": pickers,
        "rooms_groups": rooms_groups,

        "pagination_template": "default/includes/minimal_pagination.html",
    }

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

    qs = (

        FlatParams.objects

        .filter(
            flat__is_deleted=False,
        )

        .exclude(
            square__isnull=True
        )

        .exclude(
            square=0
        )
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
        .values(
            "rooms",
            "square",
            "living_square",
            "kitchen_square",

            "balcony_type__name",
            "bathroom_unit_type__name",
            "finish_type__name",

            "price_per_m2",
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
        House,
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
        FlatParams.objects
        .exclude(rooms__isnull=True)
        .values_list("rooms", flat=True)
        .distinct()
        .order_by("rooms")
    )

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