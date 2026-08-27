# apps/modules/tag_collection.py

from django.shortcuts import get_list_or_404

from .models import TagCollection, TagCollectionItem

MODULE = "default/modules/tag_collection.html"


def get_context(request, module):
    try:
        collection = TagCollection.objects.get(module=module)
    except TagCollection.DoesNotExist:
        return {"tag_collection": None}

    items = collection.items.filter(is_active=True).order_by("order", "id")
    tags = [item.tag for item in items]

    if collection.random:
        import random
        random.shuffle(tags)

    tags = tags[: collection.quantity]

    return {
        "tag_collection": collection,
        "tag_collection_tags": tags,
    }
