from django import template
from django.utils.safestring import mark_safe
from django.templatetags.static import static

from apps.maps.models import MapSettings

register = template.Library()


@register.simple_tag
def yandex_maps():
    """
    Подключает Яндекс Maps API v3 и наш JS.
    Если API не настроен — ничего не выводит.
    """

    js = static("assets/js/maps.js")

    settings = MapSettings.get_solo()

    if not settings:
        return ""

    if settings.provider != MapSettings.PROVIDER_YANDEX:
        return ""

    if not settings.api_key:
        return ""

    return mark_safe(
        f"""
<script src="https://api-maps.yandex.ru/v3/?apikey={settings.api_key}&lang=ru_RU"></script>
"""
    )