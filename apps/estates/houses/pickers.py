from apps.core.dictionaries.models import BuildingStatus
from apps.estates.houses.models import House
from apps.core.localization import t


def get_picker_label(picker, selected_values):

    default = picker.get("placeholder", picker.get("label", ""))

    if not selected_values:
        return default

    match picker["name"]:

        case "deadline_year":

            return ", ".join(
                map(str, selected_values)
            )

        case "building_status":

            labels = (
                BuildingStatus.objects
                .filter(id__in=selected_values)
                .values_list("name", flat=True)
            )

            return ", ".join(labels)

        case "phase":

            return ", ".join(
                map(str, selected_values)
            )

        case "rooms":
            return ", ".join(map(str, selected_values))

    return default


def house_list_pickers(
    *,
    sort,
    selected_deadlines,
    selected_statuses,
    selected_phases,
):
    
    deadline_queryset = House.objects.active().available_deadline_years()

    phase_queryset = House.objects.active().available_phases()

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


def house_detail_pickers(
    *,
    sort,
    selected_rooms_alias,
    selected_floor_from,
    selected_floor_to,
    selected_ceiling_height_from,
    selected_ceiling_height_to,
    selected_square_from,
    selected_square_to,
    selected_living_square_from,
    selected_living_square_to,
    selected_kitchen_square_from,
    selected_kitchen_square_to,
    selected_balcony_type,
    selected_bathroom_unit_type,
    selected_finish_type,
    selected_haggle,
    selected_mortgage,
    price_limits,
    rooms_alias_queryset,
    balcony_type_queryset,
    bathroom_unit_type_queryset,
    finish_type_queryset,
    floor_limits,
    ceiling_height_limits,
    square_limits,
    living_square_limits,
    kitchen_square_limits,
):
    pickers = [

        # =====================================================
        # ROOMS ALIAS
        # =====================================================

        {
            "name": "rooms_alias",
            "value": selected_rooms_alias,
            "placeholder": t("text_numrooms"),
            "multiple": True,
            "auto_submit": False,
            "input_type": "checkbox",

            "options": [
                {"value": alias, "label": alias}
                for alias in rooms_alias_queryset
            ],
        },

        # =====================================================
        # BALCONY TYPE
        # =====================================================

        {
            "name": "balcony_type",
            "value": selected_balcony_type,
            "placeholder": t("text_balcony_type"),
            "multiple": True,
            "auto_submit": False,
            "input_type": "checkbox",

            "options": [
                {"value": str(item.id), "label": item.name}
                for item in balcony_type_queryset
            ],
        },

        # =====================================================
        # BATHROOM UNIT TYPE
        # =====================================================

        {
            "name": "bathroom_unit_type",
            "value": selected_bathroom_unit_type,
            "placeholder": t("text_bathroom_unit_type"),
            "multiple": True,
            "auto_submit": False,
            "input_type": "checkbox",

            "options": [
                {"value": str(item.id), "label": item.name}
                for item in bathroom_unit_type_queryset
            ],
        },

        # =====================================================
        # FINISH TYPE
        # =====================================================

        {
            "name": "finish_type",
            "value": selected_finish_type,
            "placeholder": t("text_finish_type"),
            "multiple": True,
            "auto_submit": False,
            "input_type": "checkbox",

            "options": [
                {"value": str(item.id), "label": item.name}
                for item in finish_type_queryset
            ],
        },

        # =====================================================
        # FLOOR
        # =====================================================

        {
            "name": "floor",
            "type": "range",
            "label": t("text_floor"),
            "placeholder": t("text_floor"),
            "auto_submit": True,
            "range": {
                "from_name": "floor_from",
                "to_name": "floor_to",
                "from_value": selected_floor_from,
                "to_value": selected_floor_to,
                "from_placeholder": floor_limits.get("min_floor") or "",
                "to_placeholder": floor_limits.get("max_floor") or "",
            },
        },

        # =====================================================
        # CEILING HEIGHT
        # =====================================================

        {
            "name": "ceiling_height",
            "type": "range",
            "label": t("text_ceiling_height"),
            "placeholder": t("text_ceiling_height"),
            "auto_submit": True,
            "range": {
                "from_name": "ceiling_height_from",
                "to_name": "ceiling_height_to",
                "from_value": selected_ceiling_height_from,
                "to_value": selected_ceiling_height_to,
                "from_placeholder": ceiling_height_limits.get("min_ceiling_height") or "",
                "to_placeholder": ceiling_height_limits.get("max_ceiling_height") or "",
            },
        },

        # =====================================================
        # SQUARE
        # =====================================================

        {
            "name": "square",
            "type": "range",
            "label": t("text_square"),
            "placeholder": t("text_square"),
            "auto_submit": True,
            "range": {
                "from_name": "square_from",
                "to_name": "square_to",
                "from_value": selected_square_from,
                "to_value": selected_square_to,
                "from_placeholder": square_limits.get("min_square") or "",
                "to_placeholder": square_limits.get("max_square") or "",
            },
        },

        # =====================================================
        # LIVING SQUARE
        # =====================================================

        {
            "name": "living_square",
            "type": "range",
            "label": t("text_living_square"),
            "placeholder": t("text_living_square"),
            "auto_submit": True,
            "range": {
                "from_name": "living_square_from",
                "to_name": "living_square_to",
                "from_value": selected_living_square_from,
                "to_value": selected_living_square_to,
                "from_placeholder": living_square_limits.get("min_living_square") or "",
                "to_placeholder": living_square_limits.get("max_living_square") or "",
            },
        },

        # =====================================================
        # KITCHEN SQUARE
        # =====================================================

        {
            "name": "kitchen_square",
            "type": "range",
            "label": t("text_kitchen_square"),
            "placeholder": t("text_kitchen_square"),
            "auto_submit": True,
            "range": {
                "from_name": "kitchen_square_from",
                "to_name": "kitchen_square_to",
                "from_value": selected_kitchen_square_from,
                "to_value": selected_kitchen_square_to,
                "from_placeholder": kitchen_square_limits.get("min_kitchen_square") or "",
                "to_placeholder": kitchen_square_limits.get("max_kitchen_square") or "",
            },
        },

        # =====================================================
        # HAGGLE
        # =====================================================

        {
            "name": "haggle",
            "value": selected_haggle,
            "multiple": False,
            "auto_submit": False,
            "input_type": "checkbox",
            "no_header": True,

            "options": [
                {"value": "1", "label": t("text_haggle")},
            ],
        },

        # =====================================================
        # MORTGAGE
        # =====================================================

        {
            "name": "mortgage",
            "value": selected_mortgage,
            "multiple": False,
            "auto_submit": False,
            "input_type": "checkbox",
            "no_header": True,

            "options": [
                {"value": "1", "label": t("text_mortgage")},
            ],
        },
    ]

    for picker in pickers:

        picker["selected_label"] = ", ".join(
            option["label"]
            for option in picker.get("options", [])
            if str(option["value"]) in map(str, picker.get("value", []))
        )

    return pickers