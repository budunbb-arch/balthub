# apps/estates/tags/views.py

from django.shortcuts import render, get_object_or_404

from apps.estates.projects.models import Project
from apps.core.pagination import paginate_queryset
from apps.estates.projects.pickers import project_list_pickers
from apps.core.engines.picker import normalize_querydict
from .models import Tag


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

    sort = state.get("sort", ["name"])[0]

    qs = (
        Project.objects
        .active()
        .filter(tags=tag)
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

    page_obj, paginator, page_range = paginate_queryset(
        request,
        qs,
        12,
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
        "tag": tag,
    }

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
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
