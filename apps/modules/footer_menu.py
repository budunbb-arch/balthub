# /opt/balthub/apps/modules/footer_menu.py

from .models import FooterMenuItem

MODULE = "default/modules/footer_menu.html"


def get_context(request, module):
    items = FooterMenuItem.objects.filter(module=module, is_active=True).order_by("order", "id")
    return {"footer_menu_items": items}
