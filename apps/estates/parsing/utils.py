# /opt/balthub/apps/estates/parsing/utils.py

import re
import hashlib

from django.utils import timezone
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

    text = text.replace("\r", "\n")

    parts = [part.strip() for part in re.split(r"\n+", text) if part.strip()]

    return "".join(f"<p>{part}</p>" for part in parts)


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


def cache_key(value: str) -> str:
    if not value:
        return ""

    return value.strip().lower()