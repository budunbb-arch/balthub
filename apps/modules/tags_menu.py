# /opt/balthub/apps/modules/tags_menu.py

from .models import TagsMenu

MODULE = "default/modules/tags_menu.html"


def get_context(request, module):
    try:
        tags_menu = TagsMenu.objects.get(module=module)
    except TagsMenu.DoesNotExist:
        return {"tags_menu": None}

    items = tags_menu.items.filter(is_active=True).order_by("order", "id")
    return {
        "tags_menu": tags_menu,
        "tags_menu_items": items,
    }
