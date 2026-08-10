# apps/leads/feedback_module.py

from .models import FeedbackModule
from apps.core.common.models import Module
from apps.core.dictionaries.models import Country
from apps.core.models import SiteSettings
from .turnstile import is_turnstile_enabled


MODULE = "default/modules/feedback.html"


import logging

logger = logging.getLogger(__name__)


# Сопоставление контактного типа -> (name-атрибут input, HTML-тип input).
# ВАЖНО: в БД у ContactType поле 'code' хранит иконку FontAwesome
# (напр. "fa-solid fa-square-phone"), а семантическое имя ("telephone",
# "email", ...) лежит в поле 'name'. Поэтому распознаём по 'name'
# (в нижнем регистре), с запасным поиском по подстроке в 'code'/'name'.
CONTACT_FIELD_SPECS = {
    "telephone": {"input_name": "phone", "input_type": "tel"},
    "whatsapp": {"input_name": "phone", "input_type": "tel"},
    "email": {"input_name": "email", "input_type": "email"},
    "telegram": {"input_name": "telegram", "input_type": "text"},
    "max": {"input_name": "max", "input_type": "text"},
}


def _build_contact_fields(feedback):
    """Вернуть список полей контактов для формы обратной связи."""
    if feedback is None:
        return []

    fields = []
    for contact_type in feedback.contact_types.all():
        name = (contact_type.name or "").strip().lower()
        spec = CONTACT_FIELD_SPECS.get(name)

        if spec is None:
            haystack = f"{contact_type.name or ''} {contact_type.code or ''}".lower()
            spec = next(
                (s for key, s in CONTACT_FIELD_SPECS.items() if key in haystack),
                None,
            )

        if spec is None:
            spec = {
                "input_name": (contact_type.name or "value").strip(),
                "input_type": "text",
            }

        fields.append(
            {
                "input_name": spec["input_name"],
                "input_type": spec["input_type"],
                "placeholder": contact_type.name,
            }
        )
    return fields


def get_context(request, module):
    logger.info("[FEEDBACK MODULE] module_id=%s type=%s template=%s", getattr(module, "id", None), getattr(module, "type", None), getattr(module, "template", None))
    feedback = None
    feedbacks = getattr(module, "feedback_modules", None)
    if feedbacks is not None and feedbacks.exists():
        feedback = feedbacks.first()
    else:
        if isinstance(module, Module):
            feedback = FeedbackModule.objects.filter(module=module).first()
            if feedback is None:
                feedback = FeedbackModule.objects.create(module=module)
    logger.info("[FEEDBACK MODULE] feedback_id=%s", getattr(feedback, "id", None))
    contact_fields = _build_contact_fields(feedback)
    return {
        "feedback": feedback,
        "feedback_contact_fields": contact_fields,
        "has_phone": any(f["input_name"] == "phone" for f in contact_fields),
        "phone_countries": list(Country.objects.all().values("code", "name", "phone_code")),
        "turnstile_site_key": (
            SiteSettings.get_solo().turnstile_site_key
            if is_turnstile_enabled()
            else ""
        ),
    }

