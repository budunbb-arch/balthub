# /opt/balthub/apps/modules/flat_description.py

from apps.core.common.models import Module


MODULE = "default/modules/flat_description.html"


def get_context(request, module):

    flat = getattr(request, "flat", None)

    module_obj = module
    module_id = getattr(module, "id", None)
    if module_id and not isinstance(module, Module):
        module_obj = Module.objects.filter(pk=module_id).first()

    mortgage = False
    haggle = False

    if flat is not None:
        for deal in flat.deals.all():
            if deal.mortgage:
                mortgage = True
            if deal.haggle:
                haggle = True

    return {
        "flat": flat,
        "mortgage": mortgage,
        "haggle": haggle,
    }
