from apps.core.dictionaries.models import (
    City,
    District,
    BuildingStatus
)
from apps.estates.developers.models import Developer
from apps.core.localization import t


def get_picker_label(picker, selected_values):

    default = picker.get(
        "placeholder",
        picker.get("label", "")
    )

    if not selected_values:
        return default

    match picker["name"]:

        case "developer":

            labels = (
                Developer.objects
                .filter(id__in=selected_values)
                .values_list("name", flat=True)
            )

        case "city":

            labels = (
                City.objects
                .filter(id__in=selected_values)
                .values_list("name", flat=True)
            )

        case "district":

            labels = (
                District.objects
                .filter(id__in=selected_values)
                .values_list("name", flat=True)
            )

        case "deadline_year":

            labels = map(str, selected_values)

        case "phase":

            labels = map(str, selected_values)

        case "building_status":

            labels = (
                BuildingStatus.objects
                .filter(id__in=selected_values)
                .values_list("name", flat=True)
            )

        case _:
            return default

    return ", ".join(labels)


def project_list_pickers(
    *,
    sort,
    selected_developers,
    selected_cities,
    selected_districts,
):

    district_queryset = District.objects.none()

    if selected_cities:

        district_queryset = (

            District.objects

            .filter(
                city_id__in=selected_cities
            )

            .select_related(
                "city"
            )

            .order_by(
                "name"
            )
        )

    pickers = [

        # =====================================================
        # SORT
        # =====================================================

        {
            "name": "sort",
            "value": sort,
            "placeholder": t("text_sort"),
            "auto_submit": True,
            "input_type": "radio",

            "options": [

                {
                    "value": "name",
                    "label": t("text_name_az"),
                },

                {
                    "value": "-name",
                    "label": t("text_name_za"),
                },

                {
                    "value": "city",
                    "label": t("text_city_az"),
                },

                {
                    "value": "-city",
                    "label": t("text_city_za"),
                },
            ]
        },

        # =====================================================
        # DEVELOPER
        # =====================================================

        {
            "name": "developer",
            "value": selected_developers,
            "placeholder": t("text_developer"),
            "multiple": True,
            "auto_submit": False,
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
            "value": selected_cities,
            "placeholder": t("text_city"),
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
            "placeholder": t("text_district"),
            "multiple": True,
            "disabled": not selected_cities,
            "auto_submit": False,
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


def project_detail_pickers(
    *,
    sort,
    selected_deadlines,
    selected_statuses,
    selected_phases,
    deadline_queryset,
    phase_queryset,
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
            "value": selected_deadlines,
            "placeholder": "Срок сдачи",
            "multiple": True,
            "auto_submit": False,
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
            "value": selected_statuses,
            "placeholder": "Статус",
            "multiple": True,
            "auto_submit": False,
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
            "value": selected_phases,
            "placeholder": "Очередь",
            "multiple": True,
            "auto_submit": False,
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

    for picker in pickers:

        picker["selected_label"] = get_picker_label(
            picker,
            picker.get("value", [])
        )

    return pickers