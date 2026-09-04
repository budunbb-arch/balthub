# apps/core/engines/context_processors.py

from django.core.cache import cache
from django.utils.translation import get_language

from apps.core.common.models import Module
from apps.core.localization import load_locale
from apps.core.models import SiteSettings
from apps.maps.models import MapSettings

from apps.modules.registry import MODULE_HANDLERS

from .breadcrumbs import build_breadcrumbs
from .builders import build_seo

import logging

logger = logging.getLogger(__name__)



def localization(request):

    lang = (get_language() or "ru")[:2]

    return {
        "trans": load_locale(lang)
    }

def layout_modules(request):

    resolver_match = getattr(request, "resolver_match", None)
    view_name = getattr(resolver_match, "view_name", None)

    lang = (get_language() or "ru")[:2]

    if view_name:
        cache_key = f"layout:{view_name}:{lang}"
    else:
        cache_key = f"layout:global:{lang}"

    cached = cache.get(cache_key)

    if cached is not None:
        modules_meta = cached
    else:
        modules = (
            Module.objects
            .filter(is_active=True)
            .only("id", "name", "type", "template", "position", "route", "order", "html_module_id")
            .order_by("position", "order", "id")
        )
        modules_meta = [
            {
                "id": m.id,
                "name": m.name,
                "type": m.type,
                "template": m.template,
                "position": m.position,
                "route": m.route,
                "order": m.order,
                "html_module_id": m.html_module_id,
            }
            for m in modules
        ]
        cache.set(cache_key, modules_meta, 300)

    layout = {
        "main_menu": [],
        "account_menu": [],
        "sitename": [],
        "search": [],
        "sidebar": [],
        "content_top": [],
        "content_bottom": [],
    }

    for module_meta in modules_meta:

        if module_meta["route"] and module_meta["route"] != view_name:
            continue

        # ---------------------------------------
        # Загружаем контекст модуля
        # ---------------------------------------

        data = {}

        handler = MODULE_HANDLERS.get(module_meta["template"])
        logger.info("[MODULE] template=%s handler=%s", module_meta["template"], bool(handler))

        if handler:
            try:
                module = Module(id=module_meta["id"])
                module.name = module_meta["name"]
                module.type = module_meta["type"]
                module.template = module_meta["template"]
                module.position = module_meta["position"]
                module.route = module_meta["route"]
                module.order = module_meta["order"]
                module.html_module_id = module_meta["html_module_id"]

                data = handler(
                    request=request,
                    module=module,
                )
                logger.info("[MODULE] rendered template=%s data_keys=%s", module_meta["template"], list(data.keys()) if isinstance(data, dict) else type(data).__name__)
            except Exception:
                logger.exception(
                    "[MODULE ERROR] %s",
                    module_meta["template"],
                )

        layout.setdefault(module_meta["position"], [])
        layout[module_meta["position"]].append(
            {
                "module": module_meta,
                "data": data,
                }
            )

    logger.info("[LAYOUT] content_bottom=%d", len(layout["content_bottom"]))

    return {
        "layout": layout,
    }


# ----- функции очистки кэша -----

def clear_layout_cache(pattern="layout:*"):
    """
    Удаляет все ключи layout по шаблону.
    Используется при изменении модулей или контента.
    """
    redis_client = cache.client.get_client()
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)


def breadcrumbs(request):

    lang = (get_language() or "ru")[:2]
    path = request.path_info

    cache_key = f"breadcrumbs:{path}:{lang}"

    cached = cache.get(cache_key)

    if cached is not None:
        return {"breadcrumbs": cached}

    try:
        data = build_breadcrumbs(request)

    except Exception:
        logger.exception("BREADCRUMB ERROR:")
        data = []

    cache.set(cache_key, data, 300)

    return {
        "breadcrumbs": data
    }


def seo(request):

    lang = (get_language() or "ru")[:2]
    path = request.path_info

    cache_key = f"seo:{path}:{lang}"

    cached = cache.get(cache_key)

    if cached is not None:
        return {"seo": cached}

    try:
        data = build_seo(request)

    except Exception:
        logger.exception("SEO ERROR:")
        data = {}

    cache.set(cache_key, data, 300)

    return {
        "seo": data
    }


def map_settings(request):
    cache_key = "map_settings"
    cached = cache.get(cache_key)
    if cached is not None:
        return {"map_settings": cached}
    settings = MapSettings.get_solo()
    cache.set(cache_key, settings, 600)
    return {
        "map_settings": settings
    }


def site_settings(request):
    import json
    cache_key = "site_settings"
    cached = cache.get(cache_key)
    if cached is not None:
        return {"site_settings": cached}
    settings = SiteSettings.get_solo()
    if settings and isinstance(settings.phones, str):
        try:
            settings.phones = json.loads(settings.phones)
        except (json.JSONDecodeError, TypeError):
            settings.phones = []
    if settings and not settings.phones:
        settings.phones = []
    if settings and isinstance(settings.addresses, str):
        try:
            settings.addresses = json.loads(settings.addresses)
        except (json.JSONDecodeError, TypeError):
            settings.addresses = []
    if settings and not settings.addresses:
        settings.addresses = []
    cache.set(cache_key, settings, 300)
    return {
        "site_settings": settings
    }


def order_call_modal(request):
    from apps.core.documents.models import Document
    from apps.core.models import SiteSettings

    cache_key = "order_call_modal"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    personal_data_doc = Document.objects.filter(
        document_name__icontains="персональн",
        document_public=True,
        document_status="released",
    ).first()
    policy_doc = Document.objects.filter(
        document_name__icontains="политик",
        document_public=True,
        document_status="released",
    ).first()

    ss = SiteSettings.get_solo()
    turnstile_site_key = ""
    if ss and ss.turnstile_enabled and ss.turnstile_site_key:
        from apps.leads.turnstile import is_turnstile_enabled
        if is_turnstile_enabled():
            turnstile_site_key = ss.turnstile_site_key

    result = {
        "order_call_personal_data_doc": personal_data_doc,
        "order_call_policy_doc": policy_doc,
        "order_call_turnstile_site_key": turnstile_site_key,
    }
    cache.set(cache_key, result, 300)
    return result