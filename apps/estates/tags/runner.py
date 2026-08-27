# apps/estates/tags/runner.py

import logging

from django.db import transaction
from django.contrib import messages
from django.shortcuts import render

from apps.estates.flats.models import Flat
from apps.estates.projects.models import Project

from .models import AutoTagTask, FlatTag, ProjectTag

logger = logging.getLogger(__name__)


def _normalize(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    s = str(value).strip()
    if not s:
        return ""
    s = s.replace(",", ".")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def _to_comparable(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value
    s = str(value).strip().lower()
    if not s:
        return ""
    return s


def _get_flat_value(flat, param):
    try:
        params = flat.params
    except Exception:
        return None

    if param == "rooms":
        return _normalize(params.rooms)
    if param == "square":
        return _normalize(params.square)
    if param == "floor":
        return _normalize(params.floor)
    if param == "finish_type":
        return _normalize(params.finish_type.name) if params.finish_type_id else None
    if param == "balcony_type":
        return _normalize(params.balcony_type.name) if params.balcony_type_id else None
    if param == "bathroom_unit_type":
        return _normalize(params.bathroom_unit_type.name) if params.bathroom_unit_type_id else None
    if param == "ceiling_height":
        return _normalize(params.ceiling_height)
    if param == "living_square":
        return _normalize(params.living_square)
    if param == "kitchen_square":
        return _normalize(params.kitchen_square)
    if param == "haggle":
        return "true" if flat.deals.filter(haggle=True).exists() else "false"
    if param == "mortgage":
        return "true" if flat.deals.filter(mortgage=True).exists() else "false"
    return None


def _get_project_value(project, param):
    try:
        params = project.params
    except Exception:
        return None

    if param == "city":
        value = params.city.name if params.city else None
    elif param == "district":
        value = params.district.name if params.district else None
    elif param == "property_type":
        value = params.property_type.name if params.property_type else None
    elif param == "property_category":
        value = params.property_category.name if params.property_category else None
    elif param == "haggle":
        return "true" if project.houses.filter(flats__deals__haggle=True).exists() else "false"
    elif param == "mortgage":
        return "true" if project.houses.filter(flats__deals__mortgage=True).exists() else "false"
    else:
        value = None
    return _normalize(value)


def _matches(instance, task, object_type):
    triggers = task.triggers or []
    if not triggers:
        return True

    if object_type == AutoTagTask.OBJECT_TYPE_FLAT:
        getter = _get_flat_value
    else:
        getter = _get_project_value

    for trigger in triggers:
        param = trigger.get("param")
        expected_raw = trigger.get("value")
        actual = getter(instance, param)
        if actual is None:
            return False

        expected = _normalize(expected_raw)
        actual_normalized = _normalize(actual)

        try:
            if float(expected) == float(actual_normalized):
                continue
        except (ValueError, TypeError):
            pass

        if _to_comparable(expected) == _to_comparable(actual_normalized):
            continue

        return False
    return True


@transaction.atomic
def run_autotags(task_id=None):
    tasks = AutoTagTask.objects.all()
    if task_id is not None:
        tasks = tasks.filter(pk=task_id)

    summary = {
        "tasks": 0,
        "objects_checked": 0,
        "tags_created": 0,
        "skipped": 0,
    }

    for task in tasks:
        summary["tasks"] += 1
        tag = task.tag
        if task.object_type == AutoTagTask.OBJECT_TYPE_FLAT:
            qs = (
                Flat.objects
                .select_related("params")
                .prefetch_related("flat_tags")
            )
            tag_model = FlatTag
            related_name = "flat_tags"
        else:
            qs = (
                Project.objects
                .select_related("params")
                .prefetch_related("project_tags")
            )
            tag_model = ProjectTag
            related_name = "project_tags"

        for instance in qs:
            summary["objects_checked"] += 1
            if not _matches(instance, task, task.object_type):
                summary["skipped"] += 1
                continue

            existing = getattr(instance, related_name).filter(tag=tag).exists()
            if existing:
                continue

            tag_model.objects.create(
                **{("flat" if task.object_type == AutoTagTask.OBJECT_TYPE_FLAT else "project"): instance, "tag": tag}
            )
            summary["tags_created"] += 1

    return summary
