# apps/estates/projects/views.py

from django.shortcuts import render, get_object_or_404
from django.core.cache import cache
from django.conf import settings

from apps.estates.houses.models import House
from apps.estates.projects.models import Project
from apps.core.cache_keys import project_detail_key
from apps.core.pagination import paginate_queryset
from apps.core.engines.picker import normalize_querydict
from .pickers import project_list_pickers, project_detail_pickers
from apps.maps.engine import MapEngine
import json


def project_list(request):

    state = normalize_querydict(request)

    selected_cities = state.get("city", [])
    selected_districts = state.get("district", [])
    selected_developers = state.get("developer", [])

    sort = state.get("sort", ["name"])[0]

    # =====================================================
    # QUERYSET
    # =====================================================

    qs = (

        Project.objects

        .active()

        .select_related(
            "developer",
            "params__city",
            "params__district",
        )

        .city(selected_cities)
        .district(selected_districts)
        .developer(selected_developers)

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

    pickers = project_list_pickers(

        sort=sort,

        selected_developers=selected_developers,
        selected_cities=selected_cities,
        selected_districts=selected_districts,
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
            "default/pages/estates/ajax/_project_list.html",
            context
        )

    return render(
        request,
        "default/pages/estates/project_list.html",
        context
    )


def project_detail(request, project_slug):

    project = get_object_or_404(

        Project.objects.active().only("id"),

        slug=project_slug
    )

    cache_key = project_detail_key(project.id)

    cached_project = cache.get(cache_key)

    if cached_project:

        project = cached_project

    else:

        project = (

            Project.objects.active()

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
    # QUERYSET
    # =====================================================

    houses_qs = (

        House.objects

        .active()

        .for_project(project)

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
        houses_qs,
        12
    )

    # =====================================================
    # PICKERS
    # =====================================================

    pickers = project_detail_pickers(

        sort=sort,

        selected_deadlines=selected_deadlines,
        selected_statuses=selected_statuses,
        selected_phases=selected_phases,

        deadline_queryset=project.houses.active().available_deadline_years(),
        phase_queryset=project.houses.active().available_phases(),
    )

    context = {
        "project": project,

        "page_obj": page_obj,
        "paginator": paginator,
        "page_range": page_range,

        "pickers": pickers,
    }

    houses = (
        project.houses
        .exclude(params__latitude__isnull=True)
        .exclude(params__longitude__isnull=True)
        .select_related("params")
    )

    map_points = []

    for house in houses:
        map_points.append({
            "lat": house.params.latitude,
            "lon": house.params.longitude,
            "title": house.params.address,
            "url": house.get_absolute_url(),
        })

    context["map_points"] = map_points

    context["map_points_json"] = json.dumps(
        MapEngine.project_houses(project),
        ensure_ascii=False,
    )

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
