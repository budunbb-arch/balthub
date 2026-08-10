# apps/leads/views.py

import json

from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string

from .models import FeedbackModule, Lead
from .turnstile import is_turnstile_enabled, verify_turnstile_token


@require_POST
def feedback_send(request):
    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Invalid JSON")

    module_id = data.get("module_id")
    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()
    email = (data.get("email") or "").strip()
    telegram = (data.get("telegram") or "").strip()
    max_ = (data.get("max") or "").strip()
    comment = (data.get("comment") or "").strip()
    personal_data = data.get("personal_data") in ("on", "true", "1")
    policy = data.get("policy") in ("on", "true", "1")
    message_tpl = (data.get("message_tpl") or "").strip()

    if is_turnstile_enabled():
        token = (data.get("cf-turnstile-response") or "").strip()
        if not token:
            return JsonResponse(
                {"success": False, "error": "Подтвердите, что вы не робот."}, status=400
            )
        if not verify_turnstile_token(token, request.META.get("REMOTE_ADDR")):
            return JsonResponse(
                {
                    "success": False,
                    "error": "Не удалось подтвердить капчу. Попробуйте ещё раз.",
                },
                status=400,
            )

    if not module_id:
        return JsonResponse({"success": False, "error": "Не указан модуль."}, status=400)

    try:
        feedback = FeedbackModule.objects.get(pk=module_id)
    except FeedbackModule.DoesNotExist:
        return JsonResponse({"success": False, "error": "Модуль не найден."}, status=400)

    if not name:
        return JsonResponse({"success": False, "error": "Укажите имя."}, status=400)

    if feedback.personal_data and not personal_data:
        return JsonResponse({"success": False, "error": "Требуется согласие на обработку персональных данных."}, status=400)

    if feedback.policy and not policy:
        return JsonResponse({"success": False, "error": "Требуется согласие с политикой конфиденциальности."}, status=400)

    # Build message for email/lead
    parts = []
    if message_tpl:
        parts.append(message_tpl)
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
    )

    return JsonResponse({"success": True})