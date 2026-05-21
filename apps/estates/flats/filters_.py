from django.db.models import Min, Max

from apps.core.filters import FilterField
from apps.estates.flats.models import Flat


def normalize_params(params):
    return {
        k: str(v).strip()
        for k, v in (params or {}).items()
        if v not in (None, "", " ", [])
    }


def strip_range(params):
    return {
        k: v
        for k, v in params.items()
        if k not in ("square_min", "square_max")
    }

def apply_flat_filters(qs, params, exclude=None):
    exclude = exclude or set()

    if "square_min" not in exclude:
        min_val = params.get("square_min")
        if min_val:
            qs = qs.filter(params__square__gte=float(min_val))

    if "square_max" not in exclude:
        max_val = params.get("square_max")
        if max_val:
            qs = qs.filter(params__square__lte=float(max_val))

    if "floor" not in exclude:
        if params.get("floor"):
            qs = qs.filter(params__floor=params["floor"])

    if "rooms" not in exclude:
        if params.get("rooms"):
            qs = qs.filter(params__rooms=params["rooms"])

    # ------------------
    # SORT (🔥 FIX HERE)
    # ------------------

    if "sort" not in exclude:
        sort = params.get("sort")

        if sort:
            qs = qs.order_by(sort)
        else:
            qs = qs.order_by("number")  # дефолт

    return qs


def build_choices(base_qs, ui_params, field, current_field):

    all_values = (
        base_qs
        .values_list(field, flat=True)
        .exclude(**{f"{field}__isnull": True})
        .distinct()
        .order_by(field)
    )

    result = []

    for value in all_values:
        test_params = ui_params.copy()
        test_params[current_field] = value

        #qs = apply_flat_filters(base_qs, {**params, current_field: value}, exclude={current_field})
        #qs = apply_flat_filters(base_qs, test_params)
        qs = apply_flat_filters(base_qs, test_params)

        result.append({
            "value": value,
            "label": value,
            "enabled": qs.exists(),
        })

    return result


"""
def flat_filters(house=None, params=None, base_qs=None):

    params = normalize_params(params)

    if base_qs is None:
        base_qs = Flat.objects.all()

        if house:
            base_qs = base_qs.filter(house=house)

        base_qs = base_qs.select_related("params")

    # ❗ отдельно чистый qs для range
    #qs_for_range = apply_flat_filters(base_qs, strip_range(params))
    # qs_for_range = base_qs

    ui_params = params.copy()
    ui_params.pop("square_min", None)
    ui_params.pop("square_max", None)

    qs_for_range = apply_flat_filters(base_qs, params)

    agg = qs_for_range.aggregate(
        min_sq=Min("params__square"),
        max_sq=Max("params__square"),
    )

    range_min = agg["min_sq"] or 0
    range_max = agg["max_sq"] or 0

    selected_min = float(params.get("square_min") or range_min)
    selected_max = float(params.get("square_max") or range_max)

    floors = build_choices(base_qs, ui_params, "params__floor", "floor")
    rooms = build_choices(base_qs, ui_params, "params__rooms", "rooms")

    return [
        FilterField("floor", "params__floor", source=floors, label="Этаж"),
        FilterField("rooms", "params__rooms", source=rooms, label="Комнат"),

        FilterField(
            name="square",
            field_type="range",
            label="Площадь",
            extra={
                "min": float(range_min),
                "max": float(range_max),
                "value_min": selected_min,
                "value_max": selected_max,
                "step": 0.01,
            }
        ),

        FilterField(
            name="sort",
            field_type="ordering",
            choices=[
                ("number", "Number ↑"),
                ("-number", "Number ↓"),
                ("params__rooms", "Комнаты ↑"),
                ("-params__rooms", "Комнаты ↓"),
                ("params__square", "Площадь ↑"),
                ("-params__square", "Площадь ↓"),
            ],
        ),
    ]
"""

def flat_filters(house=None, params=None, base_qs=None):

    params = normalize_params(params)

    if base_qs is None:
        base_qs = Flat.objects.all()

        if house:
            base_qs = base_qs.filter(house=house)

        base_qs = base_qs.select_related("params")

    # -------------------------
    # UI PARAMS (без range)
    # -------------------------
    ui_params = params.copy()
    ui_params.pop("square_min", None)
    ui_params.pop("square_max", None)

    # -------------------------
    # RANGE DATASET
    # -------------------------
    qs_for_range = apply_flat_filters(base_qs, params)

    agg = qs_for_range.aggregate(
        min_sq=Min("params__square"),
        max_sq=Max("params__square"),
    )

    range_min = agg["min_sq"] or 0
    range_max = agg["max_sq"] or 0

    selected_min = float(params.get("square_min") or range_min)
    selected_max = float(params.get("square_max") or range_max)

    # -------------------------
    # CHOICES (ВАЖНО: ui_params)
    # -------------------------
    floors = build_choices(base_qs, ui_params, "params__floor", "floor")
    rooms = build_choices(base_qs, ui_params, "params__rooms", "rooms")

    return [
        FilterField("floor", "params__floor", source=floors, label="Этаж"),
        FilterField("rooms", "params__rooms", source=rooms, label="Комнат"),

        FilterField(
            name="square",
            field_type="range",
            label="Площадь",
            extra={
                "min": float(range_min),
                "max": float(range_max),
                "value_min": selected_min,
                "value_max": selected_max,
                "step": 0.01,
            }
        ),

        FilterField(
            name="sort",
            field_type="ordering",
            choices=[
                ("number", "Number ↑"),
                ("-number", "Number ↓"),
                ("params__rooms", "Комнаты ↑"),
                ("-params__rooms", "Комнаты ↓"),
                ("params__square", "Площадь ↑"),
                ("-params__square", "Площадь ↓"),
            ],
        ),
    ]