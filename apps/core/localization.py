# /opt/balthub/apps/core/localization.py

from pathlib import Path
from importlib import import_module

from django.conf import settings
from django.utils.translation import get_language


CACHE = {}


def discover_sections(lang):

    base = settings.BASE_DIR / "localizations" / lang

    sections = []

    for file in base.rglob("*.py"):

        if file.name == "__init__.py":
            continue

        relative = file.relative_to(base)

        section = ".".join(
            relative.with_suffix("").parts
        )

        sections.append(section)

    return sections


def load_locale(lang):

    if lang in CACHE:
        return CACHE[lang]

    data = {}

    for section in discover_sections(lang):

        try:

            module = import_module(
                f"localizations.{lang}.{section}"
            )

            data.update(module.translations)

        except Exception as e:

            print(f"[LOCALE ERROR] {section}: {e}")

    CACHE[lang] = data

    return data


def t(key):

    lang = (get_language() or "ru")[:2]

    data = load_locale(lang)

    return data.get(key, f"[{key}]")