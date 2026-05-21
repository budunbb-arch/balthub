from apps.core.filters import FilterField, FilterSet
from apps.estates.houses.models import House


def normalize_params(params):
    return {
        k: str(v).strip()
        for k, v in (params or {}).items()
        if v not in (None, "", " ", [])
    }

def build_choices(base_qs, params, field, current_field):
    all_values = (
        base_qs
        .values_list(field, flat=True)
        .exclude(**{f"{field}__isnull": True})
        .distinct()
        .order_by(field)
    )

    result = []

    for value in all_values:

        test_params = params.copy()
        test_params[current_field] = value

        # 🔥 ВАЖНО: фильтруем через полный pipeline
        qs = apply_house_filters(base_qs, test_params)

        result.append({
            "value": value,
            "label": value,
            "enabled": qs.exists(),
        })

    return result

def apply_house_filters(qs, params):
    for key, value in params.items():

        value = str(value).strip()

        if not value:
            continue

        if key == "phase":
            qs = qs.filter(params__phase__iexact=value)

        elif key == "deadline_year":
            if value.isdigit():
                qs = qs.filter(params__deadline_year=int(value))

        elif key == "floors":
            if value.isdigit():
                qs = qs.filter(params__floors=int(value))

    return qs

def house_filters(project=None, params=None, base_qs=None):

    if base_qs is None:
        base_qs = House.objects.all()

        if project:
            base_qs = base_qs.filter(project=project)

        base_qs = base_qs.select_related("params")

    params = normalize_params(params)

    # 🔥 СНАЧАЛА создаём поля
    fields = [
        FilterField(name="phase", lookup="params__phase"),
        FilterField(name="deadline_year", lookup="params__deadline_year"),
        FilterField(name="floors", lookup="params__floors"),
        FilterField(
            name="sort",
            field_type="ordering",
            choices=[
                ("params__deadline_year", "Срок сдачи ↑"),
                ("-params__deadline_year", "Срок сдачи ↓"),
                ("params__floors", "Этажность ↑"),
                ("-params__floors", "Этажность ↓"),
            ],
        ),
    ]

    phases = build_choices(base_qs, params, "params__phase", "phase")
    years = build_choices(base_qs, params, "params__deadline_year", "deadline_year")
    floors = build_choices(base_qs, params, "params__floors", "floors")

    return [
        FilterField("phase", "params__phase", source=phases, label="Очередь"),
        FilterField("deadline_year", "params__deadline_year", source=years, label="Год сдачи"),
        FilterField("floors", "params__floors", source=floors, label="Этажность"),
        fields[-1],  # sort
    ]