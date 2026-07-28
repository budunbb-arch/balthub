# /opt/balthub/apps/estates/developers/views.py

from django.shortcuts import render, get_object_or_404

from apps.core.pagination import paginate_queryset

from apps.estates.developers.models import Developer
from apps.core.dictionaries.models import City, PropertyCategory, District
from apps.core.engines.picker import normalize_querydict
from apps.estates.houses.models import House
from apps.estates.projects.models import Project
from .pickers import developer_list_pickers, developer_detail_pickers


def developer_list(request):

    state = normalize_querydict(request)

    def get_state_value(key, default=""):

        value = state.get(key, default)

        if isinstance(value, list):
            return value[0] if value else default

        return value

    selected_cities = state.get("city", [])
    selected_categories = state.get("property_category", [])
    sort = get_state_value("sort", "name")

    price_from = get_state_value("price_from")
    price_to = get_state_value("price_to")

    # =====================================================
    # BASE QUERYSET
    # =====================================================

    qs = (

        Developer.objects

        .active()

        .cities(selected_cities)

        .property_categories(selected_categories)

        .with_list_stats()

        .min_price_from(price_from)

        .min_price_to(price_to)

        .sorted(sort)

        .distinct()
    )
        

    # =====================================================
    # PAGINATION
    # =====================================================

    page_obj, paginator, page_range = paginate_queryset(request, qs, 12)


    # =====================================================
    # PICKER
    # =====================================================

    price_limits = qs.price_limits()

    print(qs.query)
    print(price_limits)

    pickers = developer_list_pickers(

        sort=sort,

        selected_cities=selected_cities,
        selected_categories=selected_categories,

        price_limits=price_limits,

        price_from=price_from,
        price_to=price_to,
    )


    # =====================================================
    # CONTEXT
    # =====================================================

    context = {
        "page_obj": page_obj,
        "paginator": paginator,
        "page_range": page_range,
        "current_sort":sort,
        "pickers": pickers,
    }

    # =====================================================
    # AJAX / FULL
    # =====================================================

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render(
            request,
            "default/pages/estates/ajax/_developer_list.html",
            context
        )

    return render(
        request,
        "default/pages/estates/developer_list.html",
        context
    )


# =========================================================
# DETAIL
# =========================================================

def developer_detail(request, slug):

    developer = get_object_or_404(

        Developer.objects

        .active()
        .detail(),

        slug=slug,
    )

    # =====================================================
    # MAP
    # =====================================================

    house_map_points = list(
        House.objects
        .active()
        .for_developer(developer)
        .exclude(params__latitude__isnull=True)
        .exclude(params__longitude__isnull=True)
        .select_related("params", "project")
        .order_by("-id")
    )

    map_points = [
        {
            "lat": h.params.latitude,
            "lon": h.params.longitude,
            "title": h.params.address or str(h),
            "url": h.get_absolute_url(),
        }
        for h in house_map_points
    ]

    # =====================================================
    # PROJECTS
    # =====================================================

    state = normalize_querydict(request)

    selected_categories = state.get("property_category", [])
    selected_cities = state.get("city", [])
    selected_districts = state.get("district", [])
    sort = state.get("sort", ["name"])[0]

    projects_qs = (

        Project.objects

        .active()

        .for_developer(developer)

        .property_categories(selected_categories)

        .cities(selected_cities)

        .districts(selected_districts)

        .select_related(
            "developer",
            "params__city",
            "params__district",
        )

        .prefetch_related(
            "images"
        )

        .sorted(sort)

        .distinct()
    )

    page_obj, paginator, page_range = paginate_queryset(
        request,
        projects_qs,
        12
    )

    pickers = developer_detail_pickers(

        sort=sort,

        selected_categories=selected_categories,
        selected_cities=selected_cities,
        selected_districts=selected_districts,
    )

    # =====================================================
    # STATS
    # =====================================================

    stats = {
        "total_projects": developer.projects_count,
        "total_houses": developer.houses_count,
        "total_flats": developer.flats_count,
        "min_price": developer.min_price,
        "max_price": developer.max_price,
    }

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {
        "developer": developer,

        "page_obj": page_obj,
        "paginator": paginator,
        "page_range": page_range,
        "pickers": pickers,

        "stats": stats,

        "map_points": map_points,
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
        "default/pages/estates/developer_detail.html",
        context
    )