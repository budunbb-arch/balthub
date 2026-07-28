# apps/core/engines/context_processors.py

from django.core.cache import cache
from django.utils.translation import get_language

from apps.core.common.models import Module
from apps.core.localization import load_locale
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

    layout = {
        "main_menu": [],
        "account_menu": [],
        "sidebar": [],
        "content_top": [],
        "content_bottom": [],
    }

    modules = (
        Module.objects
        .filter(is_active=True)
        .order_by("position", "order", "id")
    )

    for module in modules:

        if module.route and module.route != view_name:
            continue

        # ---------------------------------------
        # Загружаем контекст модуля
        # ---------------------------------------

        data = {}

        handler = MODULE_HANDLERS.get(module.template)

        if handler:
            try:
                data = handler(
                    request=request,
                    module=module,
                )
            except Exception:
                logger.exception(
                    "[MODULE ERROR] %s",
                    module.template,
                )

        layout[module.position].append(
            {
                "module": module,
                "data": data,
                }
            )

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

    try:
        data = build_breadcrumbs(request)

    except Exception:
        logger.exception("BREADCRUMB ERROR:")
        data = []

    return {
        "breadcrumbs": data
    }


def seo(request):

    try:
        data = build_seo(request)

    except Exception:
        logger.exception("SEO ERROR:")
        data = {}

    return {
        "seo": data
    }


def map_settings(request):
    return {
        "map_settings": MapSettings.get_solo(),
    }