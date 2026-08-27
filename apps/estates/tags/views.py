# apps/estates/tags/views.py

from django.shortcuts import render, get_object_or_404

from apps.estates.flats.models import Flat
from apps.estates.projects.models import Project
from apps.core.pagination import paginate_queryset
from apps.estates.flats.pickers import flat_list_pickers, tag_detail_flat_pickers
from apps.estates.projects.pickers import project_list_pickers
from apps.core.engines.picker import normalize_querydict
from .models import Tag, AutoTagTask


def tag_list(request):
    tags = Tag.objects.all().order_by("name")
    return render(
        request,
        "default/pages/estates/tag_list.html",
        {"tags": tags},
    )


def tag_detail(request, tag_slug):

    tag = get_object_or_404(Tag, slug=tag_slug)

    state = normalize_querydict(request)

    selected_cities = state.get("city", [])
    selected_districts = state.get("district", [])
    selected_developers = state.get("developer", [])
    selected_projects = state.get("project", [])

    selected_houses = state.get("house", [])
    selected_rooms_alias = state.get("rooms_alias", [])
    selected_floor_from = state.get("floor_from", [""])[0]
    selected_floor_to = state.get("floor_to", [""])[0]
    selected_ceiling_height_from = state.get("ceiling_height_from", [""])[0]
    selected_ceiling_height_to = state.get("ceiling_height_to", [""])[0]
    selected_square_from = state.get("square_from", [""])[0]
    selected_square_to = state.get("square_to", [""])[0]
    selected_living_square_from = state.get("living_square_from", [""])[0]
    selected_living_square_to = state.get("living_square_to", [""])[0]
    selected_kitchen_square_from = state.get("kitchen_square_from", [""])[0]
    selected_kitchen_square_to = state.get("kitchen_square_to", [""])[0]
    selected_balcony_type = state.get("balcony_type", [])
    selected_bathroom_unit_type = state.get("bathroom_unit_type", [])
    selected_finish_type = state.get("finish_type", [])

    sort = state.get("sort", ["name"])[0]

    tasks = AutoTagTask.objects.filter(tag=tag)
    object_types = set(tasks.values_list("object_type", flat=True))

    is_flat_tag = AutoTagTask.OBJECT_TYPE_FLAT in object_types or tag.flat_tags.exists()
    is_project_tag = AutoTagTask.OBJECT_TYPE_PROJECT in object_types or tag.project_tags.exists()

    projects_base_qs = (
        Project.objects
        .active()
        .with_flat_stats()
        .select_related(
            "developer",
            "params__city",
            "params__district",
            "description",
        )
        .city(selected_cities)
        .district(selected_districts)
        .developer(selected_developers)
        .sorted(sort)
    )

    if is_project_tag:
        projects_qs = projects_base_qs.filter(tags=tag)
    else:
        projects_qs = projects_base_qs.none()

    if is_flat_tag:
        flat_projects_qs = projects_base_qs.filter(houses__flats__flat_tags__tag=tag).distinct()
    else:
        flat_projects_qs = projects_base_qs.none()

    projects_qs = projects_qs | flat_projects_qs
    projects_qs = projects_qs.distinct()

    flats_base_qs = (
        Flat.objects
        .active()
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
        .order_by("id")
    )

    if is_flat_tag:
        flats_qs = flats_base_qs.filter(flat_tags__tag=tag)
    else:
        flats_qs = flats_base_qs.none()

    if is_project_tag:
        project_flat_qs = flats_base_qs.filter(house__project__in=projects_qs)
    else:
        project_flat_qs = flats_base_qs.none()

    flats_qs = flats_qs | project_flat_qs
    flats_qs = flats_qs.distinct()

    if selected_cities:
        flats_qs = flats_qs.filter(house__project__params__city_id__in=selected_cities)

    if selected_districts:
        flats_qs = flats_qs.filter(house__project__params__district_id__in=selected_districts)

    if selected_projects:
        flats_qs = flats_qs.filter(house__project_id__in=selected_projects)

    if selected_houses:
        flats_qs = flats_qs.filter(house_id__in=selected_houses)

    if selected_rooms_alias:
        flats_qs = flats_qs.filter(params__rooms_alias__in=selected_rooms_alias)

    if selected_balcony_type:
        flats_qs = flats_qs.filter(params__balcony_type__in=selected_balcony_type)

    if selected_bathroom_unit_type:
        flats_qs = flats_qs.filter(params__bathroom_unit_type__in=selected_bathroom_unit_type)

    if selected_finish_type:
        flats_qs = flats_qs.filter(params__finish_type__in=selected_finish_type)

    flats_qs = (
        flats_qs
        .floor_from(selected_floor_from)
        .floor_to(selected_floor_to)
        .ceiling_height_from(selected_ceiling_height_from)
        .ceiling_height_to(selected_ceiling_height_to)
        .square_from(selected_square_from)
        .square_to(selected_square_to)
        .living_square_from(selected_living_square_from)
        .living_square_to(selected_living_square_to)
        .kitchen_square_from(selected_kitchen_square_from)
        .kitchen_square_to(selected_kitchen_square_to)
    )

    projects_page_obj, projects_paginator, projects_page_range = paginate_queryset(
        request,
        projects_qs,
        12,
    )

    flats_page_obj, flats_paginator, flats_page_range = paginate_queryset(
        request,
        flats_qs,
        12,
    )

    pickers = project_list_pickers(
        sort=sort,
        selected_developers=selected_developers,
        selected_cities=selected_cities,
        selected_districts=selected_districts,
    )

    flats_pickers = tag_detail_flat_pickers(
        selected_houses=selected_houses,
        selected_rooms_alias=selected_rooms_alias,
        selected_floor_from=selected_floor_from,
        selected_floor_to=selected_floor_to,
        selected_ceiling_height_from=selected_ceiling_height_from,
        selected_ceiling_height_to=selected_ceiling_height_to,
        selected_square_from=selected_square_from,
        selected_square_to=selected_square_to,
        selected_living_square_from=selected_living_square_from,
        selected_living_square_to=selected_living_square_to,
        selected_kitchen_square_from=selected_kitchen_square_from,
        selected_kitchen_square_to=selected_kitchen_square_to,
        selected_balcony_type=selected_balcony_type,
        selected_bathroom_unit_type=selected_bathroom_unit_type,
        selected_finish_type=selected_finish_type,
        selected_cities=selected_cities,
        selected_districts=selected_districts,
        selected_projects=selected_projects,
        flat_qs=flats_qs,
    )

    context = {
        "page_obj": projects_page_obj,
        "paginator": projects_paginator,
        "page_range": projects_page_range,
        "flats_page_obj": flats_page_obj,
        "flats_paginator": flats_paginator,
        "flats_page_range": flats_page_range,
        "pickers": pickers,
        "flats_pickers": flats_pickers,
        "tag": tag,
    }

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":

        section = request.headers.get("X-Picker-Section")
        tab = request.GET.get("tab", "projects")
        if (
            section == "flats"
            or tab == "flats"
            or "house" in request.GET
            or "rooms_alias" in request.GET
            or "floor_from" in request.GET
            or "ceiling_height_from" in request.GET
            or "square_from" in request.GET
            or "living_square_from" in request.GET
            or "kitchen_square_from" in request.GET
            or "balcony_type" in request.GET
            or "bathroom_unit_type" in request.GET
            or "finish_type" in request.GET
        ):
            return render(
                request,
                "default/pages/estates/ajax/_flat_list.html",
                context,
            )
        return render(
            request,
            "default/pages/estates/ajax/_project_list.html",
            context,
        )

    return render(
        request,
        "default/pages/estates/tag_detail.html",
        context,
    )
