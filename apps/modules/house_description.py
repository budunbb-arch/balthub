# /opt/balthub/apps/modules/house_description.py

from apps.core.common.models import Module


MODULE = "default/modules/house_description.html"


def get_context(request, module):

    house = getattr(request, "house", None)

    module_obj = module
    module_id = getattr(module, "id", None)
    if module_id and not isinstance(module, Module):
        module_obj = Module.objects.filter(pk=module_id).first()

    return {
        "house": house,
    }
