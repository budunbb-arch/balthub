# apps/core/engines/context_processors.py

from django.core.cache import cache
from django.urls import resolve
from django.conf import settings
from django.utils.translation import get_language

from apps.core.common.models import Module
from apps.core.localization import load_locale

from apps.modules.registry import MODULE_FUNCTIONS

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

    resolver_match = getattr(
        request,
        "resolver_match",
        None
    )

    view_name = getattr(
        resolver_match,
        "view_name",
        None
    )

    module_context = {}

    for module_func in MODULE_FUNCTIONS:

        try:

            module_context.update(
                module_func(request)
            )

        except Exception as e:

            logger.exception(
                "[MODULE ERROR] %s: %s",
                module_func.__name__,
                str(e)
            )

    cache_key = f"layout:{view_name}"

    layout = cache.get(cache_key)

    if layout is None:

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
            .order_by("position", "id")
        )

        for module in modules:

            if module.route:

                if module.route != view_name:
                    continue

            if module.position not in layout:
                layout[module.position] = []

            layout[module.position].append(
                module.template
            )

        cache.set(
            cache_key,
            layout,
            settings.CACHE_TTL
        )

    custom_layout = getattr(
        request,
        "layout",
        {}
    )

    layout = {
        **layout,
        **custom_layout
    }

    return {
        "layout": layout,
        **module_context,
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