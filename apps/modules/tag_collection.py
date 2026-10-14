# apps/modules/tag_collection.py

from .models import TagCollection

MODULE = "default/modules/tag_collection.html"


def get_context(request, module):
    try:
        collection = TagCollection.objects.get(module=module)
    except TagCollection.DoesNotExist:
        return {"tag_collection": None}

    items = list(
        collection.items
        .filter(is_active=True)
        .select_related("tag")
        .order_by("order", "id")
    )

    if collection.random:
        import random
        random.shuffle(items)

    items = items[: collection.quantity]

    return {
        "tag_collection": collection,
        "tag_collection_tags": [item.tag for item in items],
        "tag_collection_items": items,
    }
