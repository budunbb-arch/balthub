# /opt/balthub/apps/estates/flats/pickers.py

from django.db.models import Min, Max

from apps.estates.houses.models import House
from apps.estates.flats.models import FlatParams
from apps.core.dictionaries.models import (
    BalconyType,
    BathroomUnitType,
    FinishType,
    City,
    District,
)
from apps.estates.projects.models import Project
from apps.core.localization import t


def flat_list_pickers(
    *,
    selected_houses,
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
    project,
    flat_qs=None,
):

    houses_qs = (
        House.objects
        .filter(project=project)
        .order_by("id")
    )

    rooms_alias_qs = (
        FlatParams.objects
        .filter(flat__house__project=project)
        .exclude(rooms_alias__isnull=True)
        .exclude(rooms_alias__exact="")
        .values_list("rooms_alias", flat=True)
        .distinct()
        .order_by("rooms")
    )

    balcony_type_ids = (
        FlatParams.objects
        .filter(flat__house__project=project)
        .exclude(balcony_type__isnull=True)
        .values_list("balcony_type", flat=True)
        .distinct()
        .order_by("balcony_type")
    )
    balcony_type_qs = BalconyType.objects.filter(id__in=balcony_type_ids).order_by("-name")

    bathroom_unit_type_ids = (
        FlatParams.objects
        .filter(flat__house__project=project)
        .exclude(bathroom_unit_type__isnull=True)
        .values_list("bathroom_unit_type", flat=True)
        .distinct()
        .order_by("bathroom_unit_type")
    )
    bathroom_unit_type_qs = BathroomUnitType.objects.filter(id__in=bathroom_unit_type_ids).order_by("name")

    finish_type_ids = (
        FlatParams.objects
        .filter(flat__house__project=project)
        .exclude(finish_type__isnull=True)
        .values_list("finish_type", flat=True)
        .distinct()
        .order_by("finish_type")
    )
    finish_type_qs = FinishType.objects.filter(id__in=finish_type_ids).order_by("name")

    qs = flat_qs or (
        FlatParams.objects
        .filter(flat__house__project=project)
    )

    if flat_qs is not None:
        qs = FlatParams.objects.filter(flat__in=flat_qs)

    floor_limits = qs.aggregate(
        min_floor=Min("floor"),
        max_floor=Max("floor"),
    )
    ceiling_height_limits = (
        qs.exclude(ceiling_height=0)
        .aggregate(
            min_ceiling_height=Min("ceiling_height"),
            max_ceiling_height=Max("ceiling_height"),
        )
    )
    square_limits = qs.aggregate(
        min_square=Min("square"),
        max_square=Max("square"),
    )
    living_square_limits = qs.aggregate(
        min_living_square=Min("living_square"),
        max_living_square=Max("living_square"),
    )
    kitchen_square_limits = qs.aggregate(
        min_kitchen_square=Min("kitchen_square"),
        max_kitchen_square=Max("kitchen_square"),
    )

    pickers = [

        # =====================================================
        # HOUSE
        # =====================================================

        {
            "name": "house",
            "value": selected_houses,
            "placeholder": t("text_house"),
            "multiple": True,
            "auto_submit": False,
            "input_type": "checkbox",

            "options": [

                {
                    "value": str(house.id),
                    "label": (house.params.address or str(house.id)) + (" " + house.params.corpus if house.params.corpus else ""),
                    "image": house.image,
                }

                for house in houses_qs
            ]
        },

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

                {
                    "value": alias,
                    "label": alias,
                }

                for alias in rooms_alias_qs
            ]
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

                {
                    "value": str(item.id),
                    "label": item.name,
                }

                for item in balcony_type_qs
            ]
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

                {
                    "value": str(item.id),
                    "label": item.name,
                }

                for item in bathroom_unit_type_qs
            ]
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

                {
                    "value": str(item.id),
                    "label": item.name,
                }

                for item in finish_type_qs
            ]
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
                "from_placeholder": floor_limits.get("min_floor") or "",
                "to_placeholder": floor_limits.get("max_floor") or "",
                "from_value": selected_floor_from,
                "to_value": selected_floor_to,
            }
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
                "from_placeholder": ceiling_height_limits.get("min_ceiling_height") or "",
                "to_placeholder": ceiling_height_limits.get("max_ceiling_height") or "",
                "from_value": selected_ceiling_height_from,
                "to_value": selected_ceiling_height_to,
            }
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
                "from_placeholder": square_limits.get("min_square") or "",
                "to_placeholder": square_limits.get("max_square") or "",
                "from_value": selected_square_from,
                "to_value": selected_square_to,
            }
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
                "from_placeholder": living_square_limits.get("min_living_square") or "",
                "to_placeholder": living_square_limits.get("max_living_square") or "",
                "from_value": selected_living_square_from,
                "to_value": selected_living_square_to,
            }
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
                "from_placeholder": kitchen_square_limits.get("min_kitchen_square") or "",
                "to_placeholder": kitchen_square_limits.get("max_kitchen_square") or "",
                "from_value": selected_kitchen_square_from,
                "to_value": selected_kitchen_square_to,
            }
        },
    ]

    for picker in pickers:

        picker["selected_label"] = ", ".join(
            option["label"]
            for option in picker.get("options", [])
            if str(option["value"]) in map(str, picker.get("value", []))
        )

    return pickers


def tag_detail_flat_pickers(
    *,
    selected_houses,
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
    selected_projects,
    flat_qs,
    projects_qs=None,
):

    qs = FlatParams.objects.filter(flat__in=flat_qs)

    if projects_qs is None:
        projects_qs = (
            Project.objects
            .filter(houses__flats__in=flat_qs)
            .distinct()
            .select_related("params__city", "params__district")
            .order_by("name")
        )

    houses_qs = House.objects.none()
    if selected_projects:
        houses_qs = (
            House.objects
            .filter(project_id__in=selected_projects)
            .distinct()
            .order_by("id")
        )

    rooms_alias_qs = (
        FlatParams.objects
        .filter(flat__in=flat_qs)
        .exclude(rooms_alias__isnull=True)
        .exclude(rooms_alias__exact="")
        .values_list("rooms_alias", flat=True)
        .distinct()
        .order_by("rooms")
    )

    balcony_type_ids = (
        FlatParams.objects
        .filter(flat__in=flat_qs)
        .exclude(balcony_type__isnull=True)
        .values_list("balcony_type", flat=True)
        .distinct()
        .order_by("balcony_type")
    )
    balcony_type_qs = BalconyType.objects.filter(id__in=balcony_type_ids).order_by("-name")

    bathroom_unit_type_ids = (
        FlatParams.objects
        .filter(flat__in=flat_qs)
        .exclude(bathroom_unit_type__isnull=True)
        .values_list("bathroom_unit_type", flat=True)
        .distinct()
        .order_by("bathroom_unit_type")
    )
    bathroom_unit_type_qs = BathroomUnitType.objects.filter(id__in=bathroom_unit_type_ids).order_by("name")

    finish_type_ids = (
        FlatParams.objects
        .filter(flat__in=flat_qs)
        .exclude(finish_type__isnull=True)
        .values_list("finish_type", flat=True)
        .distinct()
        .order_by("finish_type")
    )
    finish_type_qs = FinishType.objects.filter(id__in=finish_type_ids).order_by("name")

    floor_limits = qs.aggregate(
        min_floor=Min("floor"),
        max_floor=Max("floor"),
    )
    ceiling_height_limits = (
        qs.exclude(ceiling_height=0)
        .aggregate(
            min_ceiling_height=Min("ceiling_height"),
            max_ceiling_height=Max("ceiling_height"),
        )
    )
    square_limits = qs.aggregate(
        min_square=Min("square"),
        max_square=Max("square"),
    )
    living_square_limits = (
        qs
        .aggregate(
            min_living_square=Min("living_square"),
            max_living_square=Max("living_square"),
        )
    )
    kitchen_square_limits = (
        qs
        .aggregate(
            min_kitchen_square=Min("kitchen_square"),
            max_kitchen_square=Max("kitchen_square"),
        )
    )

    pickers = [
        {
            "name": "project",
            "value": selected_projects,
            "placeholder": t("text_project"),
            "multiple": True,
            "auto_submit": False,
            "input_type": "checkbox",
            "options": [
                {
                    "value": str(project.id),
                    "label": project.name,
                }
                for project in projects_qs
            ]
        },
        {
            "name": "house",
            "value": selected_houses,
            "placeholder": t("text_house"),
            "multiple": True,
            "disabled": not selected_projects,
            "auto_submit": False,
            "input_type": "checkbox",
            "options": [
                {
                    "value": str(house.id),
                    "label": (house.params.address or str(house.id)) + (" " + house.params.corpus if house.params.corpus else ""),
                    "image": house.image,
                    "project_id": house.project_id,
                }
                for house in houses_qs
            ]
        },
        {
            "name": "rooms_alias",
            "value": selected_rooms_alias,
            "placeholder": t("text_numrooms"),
            "multiple": True,
            "auto_submit": False,
            "input_type": "checkbox",
            "options": [
                {
                    "value": alias,
                    "label": alias,
                }
                for alias in rooms_alias_qs
            ]
        },
        {
            "name": "balcony_type",
            "value": selected_balcony_type,
            "placeholder": t("text_balcony_type"),
            "multiple": True,
            "auto_submit": False,
            "input_type": "checkbox",
            "options": [
                {
                    "value": str(item.id),
                    "label": item.name,
                }
                for item in balcony_type_qs
            ]
        },
        {
            "name": "bathroom_unit_type",
            "value": selected_bathroom_unit_type,
            "placeholder": t("text_bathroom_unit_type"),
            "multiple": True,
            "auto_submit": False,
            "input_type": "checkbox",
            "options": [
                {
                    "value": str(item.id),
                    "label": item.name,
                }
                for item in bathroom_unit_type_qs
            ]
        },
        {
            "name": "finish_type",
            "value": selected_finish_type,
            "placeholder": t("text_finish_type"),
            "multiple": True,
            "auto_submit": False,
            "input_type": "checkbox",
            "options": [
                {
                    "value": str(item.id),
                    "label": item.name,
                }
                for item in finish_type_qs
            ]
        },
        {
            "name": "floor",
            "type": "range",
            "label": t("text_floor"),
            "placeholder": t("text_floor"),
            "auto_submit": True,
            "range": {
                "from_name": "floor_from",
                "to_name": "floor_to",
                "from_placeholder": floor_limits.get("min_floor") or "",
                "to_placeholder": floor_limits.get("max_floor") or "",
                "from_value": selected_floor_from,
                "to_value": selected_floor_to,
            }
        },
        {
            "name": "ceiling_height",
            "type": "range",
            "label": t("text_ceiling_height"),
            "placeholder": t("text_ceiling_height"),
            "auto_submit": True,
            "range": {
                "from_name": "ceiling_height_from",
                "to_name": "ceiling_height_to",
                "from_placeholder": ceiling_height_limits.get("min_ceiling_height") or "",
                "to_placeholder": ceiling_height_limits.get("max_ceiling_height") or "",
                "from_value": selected_ceiling_height_from,
                "to_value": selected_ceiling_height_to,
            }
        },
        {
            "name": "square",
            "type": "range",
            "label": t("text_square"),
            "placeholder": t("text_square"),
            "auto_submit": True,
            "range": {
                "from_name": "square_from",
                "to_name": "square_to",
                "from_placeholder": square_limits.get("min_square") or "",
                "to_placeholder": square_limits.get("max_square") or "",
                "from_value": selected_square_from,
                "to_value": selected_square_to,
            }
        },
        {
            "name": "living_square",
            "type": "range",
            "label": t("text_living_square"),
            "placeholder": t("text_living_square"),
            "auto_submit": True,
            "range": {
                "from_name": "living_square_from",
                "to_name": "living_square_to",
                "from_placeholder": living_square_limits.get("min_living_square") or "",
                "to_placeholder": living_square_limits.get("max_living_square") or "",
                "from_value": selected_living_square_from,
                "to_value": selected_living_square_to,
            }
        },
        {
            "name": "kitchen_square",
            "type": "range",
            "label": t("text_kitchen_square"),
            "placeholder": t("text_kitchen_square"),
            "auto_submit": True,
            "range": {
                "from_name": "kitchen_square_from",
                "to_name": "kitchen_square_to",
                "from_placeholder": kitchen_square_limits.get("min_kitchen_square") or "",
                "to_placeholder": kitchen_square_limits.get("max_kitchen_square") or "",
                "from_value": selected_kitchen_square_from,
                "to_value": selected_kitchen_square_to,
            }
        },
    ]

    for picker in pickers:
        picker["selected_label"] = ", ".join(
            option["label"]
            for option in picker.get("options", [])
            if str(option["value"]) in map(str, picker.get("value", []))
        )

    return pickers
