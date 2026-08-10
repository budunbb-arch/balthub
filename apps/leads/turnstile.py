# /opt/balthub/apps/leads/turnstile.py

import logging

import requests

from apps.core.models import SiteSettings

logger = logging.getLogger(__name__)

VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def get_turnstile_settings():
    """Вернуть настройки Turnstile из SiteSettings (или пустой объект)."""
    ss = SiteSettings.get_solo()
    return ss


def is_turnstile_enabled():
    ss = get_turnstile_settings()
    return bool(
        ss
        and ss.turnstile_enabled
        and ss.turnstile_site_key
        and ss.turnstile_secret_key
    )


def verify_turnstile_token(token, remote_ip=None):
    """Проверить токен в Cloudflare. Возвращает True/False."""
    if not is_turnstile_enabled():
        # Капча не настроена/выключена — пропускаем.
        return True

    if not token:
        logger.warning("[TURNSTILE] пустой токен")
        return False

    ss = get_turnstile_settings()
    data = {
        "secret": ss.turnstile_secret_key,
        "response": token,
    }
    if remote_ip:
        data["remoteip"] = remote_ip

    try:
        resp = requests.post(VERIFY_URL, data=data, timeout=10)
        result = resp.json() if resp.status_code == 200 else {}
        ok = bool(result.get("success"))
        if not ok:
            logger.warning(
                "[TURNSTILE] verify failed, error-codes=%s",
                result.get("error-codes"),
            )
        return ok
    except Exception:
        logger.exception("[TURNSTILE] ошибка обращения к siteverify")
        return False