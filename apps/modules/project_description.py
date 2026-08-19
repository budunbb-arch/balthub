# /opt/balthub/apps/modules/project_description.py

from apps.core.common.models import Module
from apps.core.dictionaries.models import Country
from apps.core.models import SiteSettings
from apps.leads.turnstile import is_turnstile_enabled
from .models import ProjectDescriptionSettings

MODULE = "default/modules/project_description.html"


def get_context(request, module):
    project = getattr(request, "project", None)

    module_obj = module
    module_id = getattr(module, "id", None)
    if module_id and not isinstance(module, Module):
        module_obj = Module.objects.filter(pk=module_id).first()

    settings_obj = None
    if module_obj is not None:
        settings_obj = ProjectDescriptionSettings.objects.filter(module=module_obj).first()
        if settings_obj is None:
            try:
                settings_obj = ProjectDescriptionSettings.objects.create(module=module_obj)
            except Exception:
                settings_obj = None

    turnstile_site_key = ""
    if is_turnstile_enabled():
        turnstile_site_key = SiteSettings.get_solo().turnstile_site_key

    phone_countries = list(Country.objects.all().values("code", "name", "phone_code"))

    return {
        "project": project,
        "settings": settings_obj,
        "turnstile_site_key": turnstile_site_key,
        "phone_countries": phone_countries,
        "has_phone": bool(phone_countries),
    }
