# /opt/balthub/apps/estates/developers/views.py

from django.shortcuts import render, get_object_or_404

from apps.core.pagination import paginate_queryset

from apps.estates.developers.models import Developer
from apps.core.dictionaries.models import City, PropertyCategory, District
from apps.core.engines.picker import normalize_querydict
from apps.estates.projects.models import Project


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

    pickers = [

        # =====================================================
        # SORT
        # =====================================================

        {
            "name": "sort",
            "value": sort,
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
                    "value": "projects",
                    "label": "Меньше проектов",
                },

                {
                    "value": "-projects",
                    "label": "Больше проектов",
                },

                {
                    "value": "price",
                    "label": "Сначала дешевле",
                },

                {
                    "value": "-price",
                    "label": "Сначала дороже",
                },
            ]
        },

        # =====================================================
        # CITY
        # =====================================================

        {
            "name": "city",
            "label": "Город",
            "placeholder": "Выберите города",
            "value": selected_cities,
            "multiple": True,
            "auto_submit": False,
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
        # PROPERTY CATEGORY
        # =====================================================

        {
            "name": "property_category",
            "label": "Тип недвижимости",
            "placeholder": "Тип недвижимости",
            "value": selected_categories,
            "multiple": True,
            "auto_submit": False,
            "input_type": "checkbox",
            "options": [

                {
                    "value": str(category.id),
                    "label": category.name,
                }

                for category in PropertyCategory.objects.order_by("name")
            ]
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

                "from_placeholder": int(price_limits["min_price"] or 0),
                "to_placeholder": int(price_limits["max_price"] or 0),
            }
        },
    ]


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


def get_picker_label(picker, selected_values):
    if not selected_values:
        return picker["placeholder"]

    if picker["name"] == "city":
        labels = City.objects.filter(id__in=selected_values).values_list("name", flat=True)
        return ", ".join(labels)

    if picker["name"] == "property_category":
        labels = PropertyCategory.objects.filter(id__in=selected_values).values_list("name", flat=True)
        return ", ".join(labels)

    return picker["placeholder"]


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

        {
            "name": "property_category",
            "placeholder": "Тип недвижимости",
            "auto_submit": False,
            "multiple": True,
            "input_type": "checkbox",

            "options": [

                {
                    "value": str(category.id),
                    "label": category.name,
                }

                for category in PropertyCategory.objects.order_by("name")
            ]
        },

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