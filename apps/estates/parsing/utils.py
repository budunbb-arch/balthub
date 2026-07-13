# /opt/balthub/apps/estates/parsing/utils.py

import re
import hashlib

from django.utils import timezone
from apps.core.dictionaries.models import City, District
from slugify import slugify


def generate_hash(value: str) -> str:
    if not value:
        return None

    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def extract_value_from_text(text: str, patterns: list[str]) -> str | None:
    if not text:
        return None

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()

    return None

def extract_deadline(text: str) -> str | None:
    if not text:
        return None

    patterns = [
        r"сдача:\s*(.+?)(?:\s*,|$)",
    ]

    return extract_value_from_text(text, patterns)

def normalize_value(value: str, rules: list[str] = None) -> str:
    if not value:
        return value

    rules = rules or []

    for r in rules:
        value = value.replace(r, "")

    # убрать лишние точки в конце
    value = re.sub(r"\.+$", "", value)

    return value.strip()

def normalize_deadline(value: str) -> str:
    if not value:
        return value

    # убрать лишние точки и пробелы
    value = re.sub(r"\s+", " ", value)
    value = value.strip(",")

    return value


def normalize_text_block(text: str) -> str:
    if not text:
        return text

    # убрать переносы строк и табы
    text = re.sub(r"[\r\n\t]+", " ", text)

    # убрать множественные пробелы
    text = re.sub(r"\s+", " ", text)

    return text.strip()


_DICT_CACHE = {}


def resolve_dictionary(model, value: str, mapping: dict = None):
    if not value:
        return None

    value = value.strip()

    if mapping:
        value = mapping.get(value.lower(), value)

    model_name = model.__name__

    if model_name not in _DICT_CACHE:
        _DICT_CACHE[model_name] = {}

    cache = _DICT_CACHE[model_name]
    key = value.lower()

    if key in cache:
        return cache[key]

    obj = model.objects.filter(name__iexact=value).first()

    if not obj:
        obj = model.objects.create(name=value)

    cache[key] = obj
    return obj


def resolve_district(city, name):
    if not city or not name:
        return None

    obj, _ = District.objects.get_or_create(
        city=city,
        name=name.strip()
    )
    return obj
    

def resolve_city(value: str):
    if not value:
        return None

    value = value.strip()

    # нормализация только для города
    value = value[:1].upper() + value[1:].lower()

    obj, _ = City.objects.get_or_create(
        name__iexact=value,
        defaults={"name": value}
    )

    return obj


def resolve_entity(model, value: str):
    if not value:
        return None

    obj, created = model.objects.get_or_create(
        name=value,
        defaults={
            "is_public": True,
            "published_at": timezone.now(),
        }
    )

    updated_fields = []

    # публикация для уже существующих
    if not obj.is_public:
        obj.is_public = True
        if not obj.published_at:
            obj.published_at = timezone.now()
        updated_fields += ["is_public", "published_at"]

    # slug
    if not obj.slug:
        obj.slug = slugify(obj.name)
        updated_fields.append("slug")

    if updated_fields:
        obj.save(update_fields=updated_fields)

    return obj, created

def parse_and_resolve(model, text: str, patterns: list[str], normalize_rules=None):
    raw = extract_value_from_text(text, patterns)

    if not raw:
        return None

    normalized = normalize_value(raw, normalize_rules)

    return resolve_entity(model, normalized)


def to_bool(value):
    if value is None:
        return False

    value = str(value).strip().lower()

    return value in ("1", "true", "yes")


def extract_project_description(text: str) -> str | None:
    if not text:
        return None

    match = re.search(r"Застройщик\s*[:\-].*?\.\s*", text)

    if not match:
        return None

    result = text[match.end():]

    return result.strip()
