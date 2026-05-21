# apps/projects/views.py

from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.core.cache import cache
from django.conf import settings
from django.template.loader import render_to_string
from django.http import JsonResponse

from apps.estates.projects.models import Project
from apps.core.dictionaries.models import (
    City,
    District,
    BuildingStatus
)
from apps.estates.developers.models import Developer
from apps.core.cache_keys import project_detail_key, project_list_key
from apps.core.pagination import paginate_queryset
from apps.core.engines.picker import normalize_querydict


def project_list(request):

    state = normalize_querydict(request)

    selected_cities = state.get("city", [])
    selected_districts = state.get("district", [])
    selected_developers = state.get("developer", [])

    sort = state.get("sort", ["name"])[0]

    # =====================================================
    # SORT
    # =====================================================

    allowed_sort = {
        "name": "name",
        "-name": "-name",

        "city": "params__city__name",
        "-city": "-params__city__name",
    }

    order_by = allowed_sort.get(sort, "name")

    # =====================================================
    # QUERYSET
    # =====================================================

    qs = (

        Project.objects

        .select_related(
            "developer",
            "params__city",
            "params__district",
        )

        .filter(
            is_deleted=False,
            is_public=True,
        )
    )

    filters = Q()

    if selected_cities:
        filters &= Q(
            params__city_id__in=selected_cities
        )

    if selected_districts:
        filters &= Q(
            params__district_id__in=selected_districts
        )

    if selected_developers:
        filters &= Q(
            developer_id__in=selected_developers
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
    # DISTRICTS
    # =====================================================

    district_queryset = District.objects.none()

    if selected_cities:

        district_queryset = District.objects.filter(
            city_id__in=selected_cities
        ).select_related("city")

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
                    "value": "name",
                    "label": "Название А-Я",
                },

                {
                    "value": "-name",
                    "label": "Название Я-А",
                },

                {
                    "value": "city",
                    "label": "Город А-Я",
                },

                {
                    "value": "-city",
                    "label": "Город Я-А",
                },
            ]
        },

        # =====================================================
        # DEVELOPERS
        # =====================================================

        {
            "name": "developer",
            "placeholder": "Застройщик",
            "auto_submit": False,
            "multiple": True,
            "input_type": "checkbox",

            "options": [

                {
                    "value": str(dev.id),
                    "label": dev.name,
                }

                for dev in Developer.objects.order_by("name")
            ]
        },

        # =====================================================
        # CITY
        # =====================================================

        {
            "name": "city",
            "placeholder": "Город",
            "auto_submit": False,
            "multiple": True,
            "input_type": "checkbox",

            "options": [

                {
                    "value": str(city.id),
                    "label": city.name,
                }

                for city in City.objects.order_by("name")
            ]
        },

        # =====================================================
        # DISTRICT
        # =====================================================

        {
            "name": "district",
            "placeholder": "Район",
            "auto_submit": False,
            "multiple": True,
            "disabled": not selected_cities,
            "input_type": "checkbox",

            "options": [

                {
                    "value": str(district.id),
                    "label": district.name,
                }

                for district in district_queryset.order_by("name")
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
            "default/pages/estates/ajax/_project_list.html",
            context
        )

    return render(
        request,
        "default/pages/estates/project_list.html",
        context
    )


def project_detail(request, project_slug):

    project = Project.objects.only("id").get(slug=project_slug)

    cache_key = project_detail_key(project.id)

    cached_project = cache.get(cache_key)

    if cached_project:

        project = cached_project

    else:

        project = (

            Project.objects

            .select_related(
                "developer",
                "params__city",
                "params__district"
            )

            .prefetch_related(
                "images"
            )

            .get(id=project.id)
        )

        cache.set(
            cache_key,
            project,
            settings.CACHE_TTL
        )

    # =====================================================
    # STATE
    # =====================================================

    state = normalize_querydict(request)

    selected_deadlines = state.get("deadline_year", [])
    selected_statuses = state.get("building_status", [])
    selected_phases = state.get("phase", [])

    sort = state.get("sort", ["-id"])[0]

    # =====================================================
    # SORT
    # =====================================================

    allowed_sort = {

        "-id": "-id",
        "id": "id",

        "deadline_year": "params__deadline_year",
        "-deadline_year": "-params__deadline_year",

        "floors": "params__floors",
        "-floors": "-params__floors",
    }

    order_by = allowed_sort.get(sort, "-id")

    # =====================================================
    # QUERYSET
    # =====================================================

    houses_qs = (

        project.houses

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

    houses_qs = houses_qs.filter(filters)

    houses_qs = houses_qs.order_by(order_by, "id")

    # =====================================================
    # PAGINATION
    # =====================================================

    page_obj, paginator, page_range = paginate_queryset(
        request,
        houses_qs,
        12
    )

    # =====================================================
    # PICKERS
    # =====================================================

    deadline_queryset = (

        project.houses

        .exclude(params__deadline_year__isnull=True)

        .values_list(
            "params__deadline_year",
            flat=True
        )

        .distinct()

        .order_by("params__deadline_year")
    )

    phase_queryset = (

        project.houses

        .exclude(params__phase__isnull=True)
        .exclude(params__phase__exact="")

        .values_list(
            "params__phase",
            flat=True
        )

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
        "project": project,

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
        "default/pages/estates/project_detail.html",
        context
    )
