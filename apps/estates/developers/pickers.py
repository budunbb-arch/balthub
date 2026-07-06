# apps/estates/developers/pickers.py

from apps.core.dictionaries.models import (
    City,
    District,
    PropertyCategory,
)


def get_picker_label(picker, selected_values):

    default = picker.get("placeholder", picker.get("label", ""))

    if not selected_values:
        return picker["placeholder"]

    match picker["name"]:

        case "city":

            labels = (
                City.objects
                .filter(id__in=selected_values)
                .values_list(
                    "name",
                    flat=True
                )
            )

            return ", ".join(labels)

        case "district":

            labels = (
                District.objects
                .filter(id__in=selected_values)
                .values_list("name", flat=True)
            )

        case "property_category":

            labels = (
                PropertyCategory.objects
                .filter(id__in=selected_values)
                .values_list(
                    "name",
                    flat=True
                )
            )

            return ", ".join(labels)

    return picker["placeholder"]


def developer_list_pickers(
    *,
    sort,
    selected_cities,
    selected_categories,
    price_limits,
    price_from,
    price_to,
):

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
        # PRICE
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

    for picker in pickers:

        if picker.get("input_type") != "checkbox":
            continue

        picker["selected_label"] = get_picker_label(
            picker,
            picker["value"]
        )

    return pickers


def developer_detail_pickers(
    *,
    sort,
    selected_categories,
    selected_cities,
    selected_districts,
):
    district_queryset = District.objects.none()

    if selected_cities:

        district_queryset = (
            District.objects
            .filter(city_id__in=selected_cities)
            .select_related("city")
            .order_by("name")
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
        # PROPERTY CATEGORY
        # =====================================================

        {
            "name": "property_category",
            "value": selected_categories,
            "placeholder": "Тип недвижимости",
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
        # CITY
        # =====================================================

        {
            "name": "city",
            "value": selected_cities,
            "placeholder": "Город",
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
        # DISTRICT
        # =====================================================

        {
            "name": "district",
            "value": selected_districts,
            "placeholder": "Район",
            "multiple": True,
            "auto_submit": False,
            "disabled": not selected_cities,
            "input_type": "checkbox",

            "options": [

                {
                    "value": str(district.id),
                    "label": district.name,
                }

                for district in district_queryset
            ]
        },
    ]

    for picker in pickers:

        picker["selected_label"] = get_picker_label(
            picker,
            picker.get("value", [])
        )

    return pickers