# apps/leads/views.py

import json
import logging

from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string

from .models import FeedbackModule, Lead
from .turnstile import is_turnstile_enabled, verify_turnstile_token

logger = logging.getLogger(__name__)


def _build_lead_from_payload(data, settings_obj=None):
    module_id = data.get("module_id")
    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()
    email = (data.get("email") or "").strip()
    telegram = (data.get("telegram") or "").strip()
    max_ = (data.get("max") or "").strip()
    comment = (data.get("comment") or "").strip()
    date = (data.get("date") or "").strip()
    personal_data = data.get("personal_data") in ("on", "true", "1")
    policy = data.get("policy") in ("on", "true", "1")
    message_tpl = (data.get("message_tpl") or "").strip()

    if is_turnstile_enabled():
        token = (data.get("cf-turnstile-response") or "").strip()
        if not token:
            return JsonResponse(
                {"success": False, "error": "Подтвердите, что вы не робот."}, status=400
            )
        if not verify_turnstile_token(token, data.get("remote_ip") or ""):
            return JsonResponse(
                {
                    "success": False,
                    "error": "Не удалось подтвердить капчу. Попробуйте ещё раз.",
                },
                status=400,
            )

    if not module_id:
        return JsonResponse({"success": False, "error": "Не указан модуль."}, status=400)

    if settings_obj is None:
        try:
            settings_obj = FeedbackModule.objects.get(pk=module_id)
        except FeedbackModule.DoesNotExist:
            return JsonResponse({"success": False, "error": "Модуль не найден."}, status=400)

    if not name:
        return JsonResponse({"success": False, "error": "Укажите имя."}, status=400)

    if settings_obj.personal_data and not personal_data:
        return JsonResponse({"success": False, "error": "Требуется согласие на обработку персональных данных."}, status=400)

    if settings_obj.policy and not policy:
        return JsonResponse({"success": False, "error": "Требуется согласие с политикой конфиденциальности."}, status=400)

    parts = []
    if message_tpl:
        parts.append(message_tpl)
    if date:
        parts.append(f"Дата: {date}")
    if comment:
        parts.append(comment)
    if max_:
        parts.append(f"MAX: {max_}")
    if telegram:
        parts.append(f"Telegram: {telegram}")
    if phone:
        parts.append(f"Телефон: {phone}")
    if email:
        parts.append(f"Email: {email}")
    message = "\n".join(parts)

    Lead.objects.create(
        name=name,
        phone=phone,
        email=email,
        telegram=telegram,
        max=max_,
        message=message,
        requested_date=date or None,
    )

    return JsonResponse({"success": True})


@require_POST
def feedback_send(request):
    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    return _build_lead_from_payload(data)


@require_POST
def order_call_send(request):
    data = request.POST.dict()

    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()
    personal_data = data.get("personal_data") in ("on", "true", "1")
    policy = data.get("policy") in ("on", "true", "1")

    if is_turnstile_enabled():
        token = (data.get("cf-turnstile-response") or "").strip()
        if not token:
            logger.warning("[ORDER_CALL] empty turnstile token")
            return JsonResponse(
                {"success": False, "error": "Подтвердите, что вы не робот."}, status=400
            )
        if not verify_turnstile_token(token, request.META.get("REMOTE_ADDR")):
            logger.warning("[ORDER_CALL] bad turnstile token")
            return JsonResponse(
                {
                    "success": False,
                    "error": "Не удалось подтвердить капчу. Попробуйте ещё раз.",
                },
                status=400,
            )

    if not phone:
        logger.warning("[ORDER_CALL] empty phone")
        return JsonResponse({"success": False, "error": "Укажите телефон."}, status=400)

    personal_data_doc = None
    policy_doc = None
    try:
        from apps.core.documents.models import Document
        personal_data_doc = Document.objects.filter(
            document_name__icontains="персональн",
            document_public=True,
            document_status="released",
        ).first()
        policy_doc = Document.objects.filter(
            document_name__icontains="политик",
            document_public=True,
            document_status="released",
        ).first()
    except Exception:
        logger.exception("[ORDER_CALL] failed to load documents")

    if personal_data_doc and not personal_data:
        logger.warning("[ORDER_CALL] personal_data not accepted")
        return JsonResponse(
            {"success": False, "error": "Требуется согласие на обработку персональных данных."},
            status=400,
        )

    if policy_doc and not policy:
        logger.warning("[ORDER_CALL] policy not accepted")
        return JsonResponse(
            {"success": False, "error": "Требуется согласие с политикой конфиденциальности."},
            status=400,
        )

    parts = ["Заказ звонка"]
    if name:
        parts.append(f"Имя: {name}")
    if phone:
        parts.append(f"Телефон: {phone}")
    message = "\n".join(parts)

    lead = Lead.objects.create(
        name=name,
        phone=phone,
        email="",
        telegram="",
        max="",
        message=message,
    )
    logger.info("[ORDER_CALL] created lead_id=%s", lead.pk)

    return JsonResponse({"success": True})