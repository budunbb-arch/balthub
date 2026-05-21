from django.db.models import Min, Max
from apps.estates.flats.models import Flat


def flat_filters(house=None, params=None, base_qs=None):

    ctx = FilterContext.from_params(params)

    if base_qs is None:
        base_qs = Flat.objects.all()
        if house:
            base_qs = base_qs.filter(house=house)
        base_qs = base_qs.select_related("params").prefetch_related("deals")

    engine = FilterEngine(base_qs, [], ctx)

    # -------------------
    # RANGE: SQUARE
    # -------------------
    agg_sq = engine.apply().aggregate(
        min_sq=Min("params__square"),
        max_sq=Max("params__square"),
    )

    range_sq_min = agg_sq["min_sq"] or 0
    range_sq_max = agg_sq["max_sq"] or 0

    selected_sq_min = float(ctx.raw.get("square_min") or range_sq_min)
    selected_sq_max = float(ctx.raw.get("square_max") or range_sq_max)

    # -------------------
    # RANGE: PRICE
    # -------------------
    agg_price = engine.apply().aggregate(
        min_price=Min("deals__price"),
        max_price=Max("deals__price"),
    )

    range_price_min = agg_price["min_price"] or 0
    range_price_max = agg_price["max_price"] or 0

    selected_price_min = float(ctx.raw.get("price_min") or range_price_min)
    selected_price_max = float(ctx.raw.get("price_max") or range_price_max)

    # -------------------
    # CHOICES
    # -------------------
    rooms = engine.build_choices(base_qs, "params__rooms", "rooms")

    fields = [
        FilterField("rooms", "params__rooms", source=rooms),

        # SQUARE
        FilterField(
            name="square",
            field_type="range",
            lookup="params__square",
            extra={
                "min": float(range_sq_min),
                "max": float(range_sq_max),
                "value_min": selected_sq_min,
                "value_max": selected_sq_max,
                "step": 0.01,
            }
        ),

        # PRICE
        FilterField(
            name="price",
            field_type="range",
            lookup="price",
            extra={
                "min": float(range_price_min),
                "max": float(range_price_max),
                "value_min": selected_price_min,
                "value_max": selected_price_max,
                "step": 1,
            }
        ),

        FilterField(
            name="sort",
            field_type="ordering",
            choices=[
                ("number", "Number ↑"),
                ("-number", "Number ↓"),
                ("params__rooms", "Rooms ↑"),
                ("-params__rooms", "Rooms ↓"),
                ("params__square", "Square ↑"),
                ("-params__square", "Square ↓"),
                ("price", "Price ↑"),
                ("-price", "Price ↓"),
            ],
        ),
    ]

    return {
        "fields": fields,
        "context": ctx,
    }