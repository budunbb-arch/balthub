from apps.core.dictionaries.models import BuildingStatus
from apps.estates.houses.models import House


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
    selected_rooms,
    square_from,
    square_to,
    price_from,
    price_to,
    price_limits,
    rooms_queryset,
    square_limits,
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
                {"value": "rooms", "label": "Комнаты ↑"},
                {"value": "-rooms", "label": "Комнаты ↓"},
                {"value": "square", "label": "Площадь ↑"},
                {"value": "-square", "label": "Площадь ↓"},
                {"value": "price", "label": "Цена ↑"},
                {"value": "-price", "label": "Цена ↓"},
            ],
        },

        # =====================================================
        # ROOMS
        # =====================================================
        {
            "name": "rooms",
            "value": selected_rooms,
            "placeholder": "Комнаты",
            "multiple": True,
            "auto_submit": False,
            "input_type": "checkbox",
            "options": [
                {"value": str(room), "label": str(room)}
                for room in rooms_queryset
            ],
        },

        # =====================================================
        # SQUARE RANGE
        # =====================================================
        {
            "name": "square",
            "label": "Площадь",
            "type": "range",
            "auto_submit": True,
            "range": {
                "from_name": "square_from",
                "to_name": "square_to",
                "from_value": square_from,
                "to_value": square_to,
                "from_placeholder": int(square_limits["min_square"] or 0),
                "to_placeholder": int(square_limits["max_square"] or 0),
            },
        },

        # =====================================================
        # PRICE RANGE
        # =====================================================
        {
            "name": "price",
            "label": "Цена",
            "type": "range",
            "auto_submit": True,
            "range": {
                "from_name": "price_from",
                "to_name": "price_to",
                "from_value": price_from,
                "to_value": price_to,
                "from_placeholder": int(price_limits["min_price"] or 0),
                "to_placeholder": int(price_limits["max_price"] or 0),
            },
        },
    ]

    for picker in pickers:
        picker["selected_label"] = get_picker_label(
            picker,
            picker.get("value", [])
        )

    return pickers