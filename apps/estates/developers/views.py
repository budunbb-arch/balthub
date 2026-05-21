# /opt/balthub/apps/estates/developers/views.py

from django.shortcuts import render, get_object_or_404
from django.db.models import Min, Max, Count, Prefetch, Q

from apps.core.pagination import paginate_queryset

from apps.estates.developers.models import (
    Developer,
    DeveloperContact,
    DeveloperDepartment,
    DepartmentContact,
)
from apps.core.dictionaries.models import City, PropertyCategory, District
from apps.core.engines.picker import normalize_querydict


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
    # SORT
    # =====================================================

    allowed_sort = {
        "name": "name",
        "-name": "-name",

        "projects": "projects_count",
        "-projects": "-projects_count",

        "price": "min_price",
        "-price": "-min_price",
    }

    order_by = allowed_sort.get(sort, "name")

    # =====================================================
    # BASE QUERYSET
    # =====================================================

    qs = Developer.objects.filter(
        is_deleted=False,
        is_public=True
    )

    filters = Q()

    if selected_cities:
        filters &= Q(
            projects__params__city_id__in=selected_cities
        )

    if selected_categories:
        filters &= Q(
            projects__params__property_category_id__in=selected_categories
        )

    qs = qs.filter(filters)

    qs = qs.annotate(
        projects_count=Count("projects", distinct=True),
        min_price=Min("projects__houses__flats__deals__price"),
    )

    # =====================================================
    # PRICE RANGE
    # =====================================================

    if price_from:
        qs = qs.filter(
            min_price__gte=price_from
        )

    if price_to:
        qs = qs.filter(
            min_price__lte=price_to
        )

    qs = qs.order_by(order_by, "id").distinct()
        

    # =====================================================
    # PAGINATION
    # =====================================================

    page_obj, paginator, page_range = paginate_queryset(request, qs, 12)


    # =====================================================
    # PICKER
    # =====================================================

    price_limits = qs.aggregate(
        min_price=Min("projects__houses__flats__deals__price"),
        max_price=Max("projects__houses__flats__deals__price"),
    )

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

        .annotate(

            projects_count=Count(
                "projects",
                distinct=True
            ),

            houses_count=Count(
                "projects__houses",
                distinct=True
            ),

            flats_count=Count(
                "projects__houses__flats",
                distinct=True
            ),

            min_price=Min(
                "projects__houses__flats__deals__price"
            ),

            max_price=Max(
                "projects__houses__flats__deals__price"
            ),
        )

        .prefetch_related(

            "developerdescriptions",

            Prefetch(
                "developercontacts",
                queryset=DeveloperContact.objects.select_related(
                    "contact_type"
                )
            ),

            Prefetch(
                "developerdepartments",
                queryset=DeveloperDepartment.objects.prefetch_related(

                    Prefetch(
                        "contacts",
                        queryset=DepartmentContact.objects.select_related(
                            "contact_type"
                        )
                    )

                )
            )

        ),

        slug=slug,
        is_deleted=False,
        is_public=True,
    )

    # =====================================================
    # PROJECTS
    # =====================================================

    state = normalize_querydict(request)

    selected_categories = state.get("property_category", [])
    selected_cities = state.get("city", [])
    selected_districts = state.get("district", [])
    sort = state.get("sort", ["name"])[0]

    allowed_sort = {
        "name": "name",
        "-name": "-name",

        "city": "params__city__name",
        "-city": "-params__city__name",
    }

    order_by = allowed_sort.get(sort, "name")

    projects_qs = (

        developer.projects

        .filter(
            is_deleted=False,
            is_public=True,
        )

        .select_related(
            "developer",
            "params__city",
            "params__district",
        )

        .prefetch_related(
            "images"
        )
    )

    if selected_categories:
        projects_qs = projects_qs.filter(
            params__property_category_id__in=selected_categories
        )

    if selected_cities:
        projects_qs = projects_qs.filter(
            params__city_id__in=selected_cities
        )

    if selected_districts:
        projects_qs = projects_qs.filter(
            params__district_id__in=selected_districts
        )

    projects_qs = projects_qs.order_by(order_by, "id").distinct()

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