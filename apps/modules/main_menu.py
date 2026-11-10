from urllib.parse import urlsplit

from django.utils.translation import get_language
from django.urls import NoReverseMatch, get_resolver, reverse
from django.urls.resolvers import RoutePattern, URLPattern, URLResolver

from apps.core.localization import load_locale
from .models import MainMenuItem

MODULE = "default/modules/main_menu.html"

def _named_routes(patterns, namespace=""):
    for pattern in patterns:
        if not isinstance(pattern.pattern, RoutePattern):
            continue

        route = str(pattern.pattern)
        if "<" in route:
            continue

        if isinstance(pattern, URLResolver):
            child_namespace = namespace
            if pattern.namespace:
                child_namespace = f"{namespace}{pattern.namespace}:"
            yield from _named_routes(pattern.url_patterns, child_namespace)
            continue

        if isinstance(pattern, URLPattern) and pattern.name:
            yield f"{namespace}{pattern.name}"


def get_section_url_choices():
    choices = []
    excluded_names = {"robots", "sitemap"}
    excluded_prefixes = ("/account/", "/admin/", "/api/", "/media/", "/static/")
    language = (get_language() or "ru")[:2]
    translations = load_locale(language)

    for name in sorted(set(_named_routes(get_resolver().url_patterns))):
        short_name = name.rsplit(":", 1)[-1]
        if short_name in excluded_names or short_name.endswith(("_ajax", "_send")):
            continue

        try:
            url = reverse(name)
        except NoReverseMatch:
            continue

        path = urlsplit(url).path
        if path.startswith(excluded_prefixes):
            continue
        if path in {"/robots.txt", "/sitemap.xml"}:
            continue

        label = translations.get(
            f"main_menu_section_{short_name}",
            short_name.replace("_", " "),
        )
        choice_label = translations["main_menu_section_choice"].format(
            label=label,
            url=url,
        )
        choices.append((url, choice_label))

    return [
        ("", translations["main_menu_select_section"]),
        *choices,
    ]


def get_context(request, module):
    current_path = request.path
    items = []

    for item in MainMenuItem.objects.filter(
        module=module,
        is_active=True,
    ).order_by("range", "id"):
        item_path = urlsplit(item.url).path
        is_current = item_path == current_path or (
            item_path != "/" and current_path.startswith(f"{item_path.rstrip('/')}/")
        )
        items.append({
            "name": item.name,
            "url": item.url,
            "css_class": item.css_class,
            "is_current": is_current,
        })

    return {"main_menu_items": items}
