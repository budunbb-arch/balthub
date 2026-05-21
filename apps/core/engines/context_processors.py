# apps/core/engines/context_processors.py

from django.core.cache import cache
from django.urls import resolve
from django.conf import settings
from apps.core.common.models import Module
from apps.modules.registry import MODULE_FUNCTIONS
from .breadcrumbs import build_breadcrumbs
from .builders import build_seo



def layout_modules(request):
    """
    Возвращает layout для текущей страницы.
    Кэшируется в Redis по view_name.
    Поддерживаются:
      - Глобальные модули (route=None)
      - View-specific модули (route - начало пути)
    """
    try:
        view_name = resolve(request.path).view_name
    except:
        view_name = request.path

    module_context = {}

    for module_func in MODULE_FUNCTIONS:
        try:
            module_context.update(module_func(request))
        except:
            print(F"[MODULE ERROR] {module_func.__name__}: {e}")

    cache_key = f"layout:{view_name}"
    layout = cache.get(cache_key)

    if layout is None:
        # инициализация layout
        layout = {
            "main_menu": [],
            "account_menu": [],
            "sidebar": [],
            "content_top": [],
            "content_bottom": [],
        }

        modules = Module.objects.filter(is_active=True).order_by("position", "id")

        for module in modules:
            # если route задан, показываем модуль только для пути request.path
            # иначе route=None → глобальный модуль
            # if module.route:
            #     if not request.path.startswith(module.route):
            #         continue
            view_name = resolve(request.path).view_name

            if module.route:
                if module.route != view_name:
                    continue

            layout[module.position].append(module.template)

        cache.set(cache_key, layout, settings.CACHE_TTL)

    # подмешиваем кастомный layout из view (request.layout)
    custom_layout = getattr(request, "layout", {})
    layout = {**layout, **custom_layout}

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

    except Exception as e:
        print("BREADCRUMB ERROR:", e)
        data = []

    return {
        "breadcrumbs": data
    }


def seo(request):
    return {
        "seo": build_seo(request)
    }