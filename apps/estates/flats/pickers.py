# /opt/balthub/apps/estates/flats/pickers.py

from apps.estates.houses.models import House


def flat_list_pickers(
    *,
    selected_houses,
    project,
):

    houses_qs = (
        House.objects
        .filter(project=project)
        .order_by("id")
    )

    pickers = [

        # =====================================================
        # HOUSE
        # =====================================================

        {
            "name": "house",
            "value": selected_houses,
            "placeholder": "Дом",
            "multiple": True,
            "auto_submit": False,
            "input_type": "checkbox",

            "options": [

                {
                    "value": str(house.id),
                    "label": house.params.address or str(house.id),
                }

                for house in houses_qs
            ]
        },
    ]

    for picker in pickers:

        picker["selected_label"] = ", ".join(
            option["label"]
            for option in picker["options"]
            if str(option["value"]) in map(str, picker.get("value", []))
        )

    return pickers
