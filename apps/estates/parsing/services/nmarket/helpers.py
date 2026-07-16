# apps/estates/parsing/services/nmarket/helpers.py



def get_text(parent, path, ns):
    el = parent.find(path, ns)
    return el.text.strip() if el is not None and el.text else None

def get_nested_text(parent, path, ns):
    el = parent.find(path, ns)
    return el.text.strip() if el is not None and el.text else None

def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def touch_instance(
    instance,
    created,
    stats,
    created_key,
    updated_key,
    **fields,
):
    """
    Обновляет объект только если изменились данные и ведет статистику.
    """

    changed = created

    for field, value in fields.items():
        if getattr(instance, field) != value:
            setattr(instance, field, value)
            changed = True

    if changed:
        instance.save()

    if created:
        stats[created_key] += 1
    elif changed:
        stats[updated_key] += 1

    return instance


def update_instance(instance, **fields):
    """
    Обновляет только изменившиеся поля.
    Возвращает True, если объект был изменен.
    """

    changed_fields = []

    for field, value in fields.items():
        if getattr(instance, field) != value:
            setattr(instance, field, value)
            changed_fields.append(field)

    if changed_fields:
        instance.save(update_fields=changed_fields)

    return bool(changed_fields)


def update_or_create_changed(model, lookup, defaults):
    """
    Аналог update_or_create(), но возвращает:
        (obj, created, changed)
    """

    obj, created = model.objects.get_or_create(
        **lookup,
        defaults=defaults,
    )

    if created:
        return obj, True, True

    changed = update_instance(
        obj,
        **defaults,
    )

    return obj, False, changed