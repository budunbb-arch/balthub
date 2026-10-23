import hashlib
import logging
import secrets
import smtplib
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from apps.core.dictionaries.models import ContactType
from apps.core.documents.models import Document
from apps.core.localization import t
from apps.leads.captcha import create_challenge, verify_challenge
from apps.leads.turnstile import is_turnstile_enabled, verify_turnstile_token

from .models import AccountAccount, AccountAccountGroup, AccountGroup

logger = logging.getLogger(__name__)

ACTIVATION_LIFETIME = timedelta(hours=1)
PASSWORD_RESET_LIFETIME = timedelta(hours=1)
PASSWORD_RESET_MESSAGE = t("passreset_hint")
PASSWORD_REQUIREMENTS_MESSAGE = t("password_requirements")


def _validate_account_password(password, user=None):
    if len(password) < 8 or len(password) > 1024:
        return t("password_requirements")
    if not any(character.isupper() for character in password):
        return PASSWORD_REQUIREMENTS_MESSAGE
    if not any(character.islower() for character in password):
        return PASSWORD_REQUIREMENTS_MESSAGE
    if not any(character in "0123456789" for character in password):
        return PASSWORD_REQUIREMENTS_MESSAGE
    try:
        validate_password(password, user=user)
    except ValidationError as error:
        return " ".join(error.messages)
    return None


def _registration_response(request, data, status=200):
    data["captcha"] = create_challenge(request)
    return JsonResponse(data, status=status)


def _account_response(request, data, status=200):
    return _registration_response(request, data, status)


def _get_email_contact_type():
    contact_types = list(ContactType.objects.filter(
        Q(name__iexact=t("text_email_variant0"))
        | Q(name__iexact=t("text_email_variant1"))
        | Q(name__iexact=t("text_email_variant2"))
        | Q(name__iexact=t("text_email_variant3"))
    ))
    return contact_types[0] if len(contact_types) == 1 else None


def _accounts_by_email(email_contact_type, email):
    return AccountAccount.objects.filter(
        contacts__contains={str(email_contact_type.pk): email}
    )


def _get_account_by_email(email_contact_type, email):
    return (
        _accounts_by_email(email_contact_type, email)
        .order_by("pk")
        .first()
    )


@require_POST
def account_login(request):
    data = request.POST
    if not verify_challenge(
        request,
        data.get("captcha_id"),
        data.get("captcha_value"),
    ):
        return _account_response(
            request,
            {"success": False, "error": t("text_notbot")},
            status=400,
        )

    if is_turnstile_enabled():
        token = (data.get("cf-turnstile-response") or "").strip()
        if not verify_turnstile_token(token, request.META.get("REMOTE_ADDR")):
            return _account_response(
                request,
                {
                    "success": False,
                    "error": t("captcha_error"),
                },
                status=400,
            )

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if len(password) > 1024:
        return _account_response(
            request,
            {
                "success": False,
                "error": t("login_error"),
            },
            status=400,
        )
    try:
        validate_email(email)
    except ValidationError:
        return _account_response(
            request,
            {"success": False, "error": t("login_error")},
            status=400,
        )

    email_contact_type = _get_email_contact_type()
    if email_contact_type is None:
        logger.error("Account login requires exactly one email contact type.")
        return _account_response(
            request,
            {"success": False, "error": t("login_restricted")},
            status=503,
        )

    account = _get_account_by_email(email_contact_type, email)
    if not account or not account.active or not check_password(password, account.password):
        return _account_response(
            request,
            {"success": False, "error": t("login_error")},
            status=400,
        )

    request.session.cycle_key()
    request.session["account_id"] = account.pk
    request.session.set_expiry(0)
    return _account_response(
        request,
        {
            "success": True,
            "next_url": reverse("account_dashboard"),
        },
    )


@require_GET
def account_dashboard(request):
    account_id = request.session.get("account_id")
    if not isinstance(account_id, int) or account_id <= 0:
        return redirect("home")

    account = (
        AccountAccount.objects
        .filter(pk=account_id, active=True)
        .prefetch_related("groups")
        .first()
    )
    if account is None:
        request.session.pop("account_id", None)
        return redirect("home")

    email_contact_type = _get_email_contact_type()
    email = (
        account.contacts.get(str(email_contact_type.pk), "")
        if email_contact_type
        else ""
    )
    return render(
        request,
        "default/pages/account_dashboard.html",
        {
            "account": account,
            "account_email": email,
            "account_groups": account.groups.all(),
        },
    )


@require_POST
def account_logout(request):
    request.session.flush()
    return redirect("home")


@require_POST
def account_password_reset_request(request):
    data = request.POST
    if not verify_challenge(
        request,
        data.get("captcha_id"),
        data.get("captcha_value"),
    ):
        return _account_response(
            request,
            {"success": False, "error": t("text_notbot")},
            status=400,
        )

    if is_turnstile_enabled():
        token = (data.get("cf-turnstile-response") or "").strip()
        if not verify_turnstile_token(token, request.META.get("REMOTE_ADDR")):
            return _account_response(
                request,
                {
                    "success": False,
                    "error": t("captcha_error"),
                },
                status=400,
            )

    email = (data.get("email") or "").strip().lower()
    try:
        validate_email(email)
    except ValidationError:
        return _account_response(
            request,
            {"success": True, "message": PASSWORD_RESET_MESSAGE},
        )

    email_contact_type = _get_email_contact_type()
    if email_contact_type is None:
        logger.error("Password reset requires exactly one email contact type.")
        return _account_response(
            request,
            {"success": False, "error": t("reset_restricted")},
            status=503,
        )

    account = _get_account_by_email(email_contact_type, email)
    if account is None or not account.active:
        return _account_response(
            request,
            {"success": True, "message": PASSWORD_RESET_MESSAGE},
        )

    token = secrets.token_urlsafe(32)
    expires_at = timezone.now() + PASSWORD_RESET_LIFETIME
    account.secret = hashlib.sha256(token.encode("utf-8")).hexdigest()
    account.secret_idle = expires_at
    account.save(update_fields=("secret", "secret_idle"))

    reset_url = request.build_absolute_uri(
        reverse("account_password_reset", kwargs={"token": token})
    )
    message = render_to_string(
        "default/emails/account_password_reset.txt",
        {
            "name": account.name,
            "reset_url": reset_url,
            "expires_at": expires_at,
        },
    )
    try:
        sent = send_mail(
            subject=t("subject_reset"),
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        if sent != 1:
            raise smtplib.SMTPException("Password reset email was not accepted.")
    except (OSError, smtplib.SMTPException, TimeoutError):
        logger.exception("Failed to send account password reset email.")

    return _account_response(
        request,
        {"success": True, "message": PASSWORD_RESET_MESSAGE},
    )


@require_http_methods(["GET", "POST"])
def account_password_reset(request, token):
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    if request.method == "GET":
        can_reset = AccountAccount.objects.filter(
            secret=token_hash,
            secret_idle__gt=timezone.now(),
            active=True,
        ).exists()
        return render(
            request,
            "default/pages/account_password_reset.html",
            {"can_reset": can_reset, "token": token if can_reset else ""},
            status=200 if can_reset else 400,
        )

    token_is_valid = AccountAccount.objects.filter(
        secret=token_hash,
        secret_idle__gt=timezone.now(),
        active=True,
    ).exists()
    if not token_is_valid:
        return render(
            request,
            "default/pages/account_password_reset.html",
            {"can_reset": False, "token": ""},
            status=400,
        )

    password = request.POST.get("password") or ""
    password_confirm = request.POST.get("password_confirm") or ""
    if password != password_confirm:
        return render(
            request,
            "default/pages/account_password_reset.html",
            {
                "can_reset": True,
                "token": token,
                "error": t("password_mismatch"),
            },
            status=400,
        )
    password_error = _validate_account_password(password)
    if password_error:
        return render(
            request,
            "default/pages/account_password_reset.html",
            {
                "can_reset": True,
                "token": token,
                "error": password_error,
            },
            status=400,
        )

    with transaction.atomic():
        account = (
            AccountAccount.objects
            .select_for_update()
            .filter(
                secret=token_hash,
                secret_idle__gt=timezone.now(),
                active=True,
            )
            .first()
        )
        if account is None:
            return render(
                request,
                "default/pages/account_password_reset.html",
                {"can_reset": False, "token": ""},
                status=400,
            )

        account.password = make_password(password)
        account.secret = ""
        account.secret_idle = None
        account.save(update_fields=("password", "secret", "secret_idle"))

    return render(
        request,
        "default/pages/account_password_reset.html",
        {"completed": True, "can_reset": False},
    )


def _get_consent_documents():
    documents = Document.objects.filter(
        document_public=True,
        document_status="released",
    )
    return (
        documents.filter(document_name__icontains="персональн").first(),
        documents.filter(document_name__icontains="политик").first(),
    )


@require_POST
def account_register(request):
    data = request.POST
    if not verify_challenge(
        request,
        data.get("captcha_id"),
        data.get("captcha_value"),
    ):
        return _registration_response(
            request,
            {"success": False, "error": t("text_notbot")},
            status=400,
        )

    if is_turnstile_enabled():
        token = (data.get("cf-turnstile-response") or "").strip()
        if not verify_turnstile_token(token, request.META.get("REMOTE_ADDR")):
            return _registration_response(
                request,
                {
                    "success": False,
                    "error": t("captcha_error"),
                },
                status=400,
            )

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    password_confirm = data.get("password_confirm") or ""

    if not name or len(name) > 255 or len(name.split()) < 2:
        return _registration_response(
            request,
            {
                "success": False,
                "error": t("username_required"),
            },
            status=400,
        )

    try:
        validate_email(email)
    except ValidationError:
        return _registration_response(
            request,
            {"success": False, "error": t("email_requirements")},
            status=400,
        )

    email_contact_type = _get_email_contact_type()
    if email_contact_type is None:
        logger.error("Registration requires exactly one email contact type.")
        return _registration_response(
            request,
            {"success": False, "error": t("register_restricted")},
            status=503,
        )

    email_key = str(email_contact_type.pk)
    matching_accounts = _accounts_by_email(email_contact_type, email)
    if matching_accounts.filter(active=True).exists():
        return _registration_response(
            request,
            {"success": False, "error": t("email_already_registered")},
            status=409,
        )
    account = matching_accounts.filter(active=False).order_by("pk").first()

    if password != password_confirm:
        return _registration_response(
            request,
            {"success": False, "error": t("password_mismatch")},
            status=400,
        )

    password_error = _validate_account_password(password)
    if password_error:
        return _registration_response(
            request,
            {"success": False, "error": password_error},
            status=400,
        )

    personal_data_doc, policy_doc = _get_consent_documents()
    accepted = lambda key: data.get(key) in {"on", "true", "1"}
    if personal_data_doc and not accepted("personal_data"):
        return _registration_response(
            request,
            {"success": False, "error": t("persdata_required")},
            status=400,
        )
    if policy_doc and not accepted("policy"):
        return _registration_response(
            request,
            {"success": False, "error": t("policy_required")},
            status=400,
        )

    try:
        default_group = AccountGroup.objects.get(pk=1)
    except AccountGroup.DoesNotExist:
        logger.error("Registration requires account group id=1 named Пользователь.")
        return _registration_response(
            request,
            {"success": False, "error": t("register_restricted")},
            status=503,
        )
    if default_group.name.strip().casefold() != "пользователь":
        logger.error("Registration requires account group id=1 named Пользователь.")
        return _registration_response(
            request,
            {"success": False, "error": t("register_restricted")},
            status=503,
        )

    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    expires_at = timezone.now() + ACTIVATION_LIFETIME

    try:
        with transaction.atomic():
            if account is None:
                account = AccountAccount.objects.create(
                    name=name,
                    password=make_password(password),
                    active=False,
                    contacts={email_key: email},
                    secret=token_hash,
                    secret_idle=expires_at,
                )
            else:
                account.secret = token_hash
                account.secret_idle = expires_at
                account.save(update_fields=("secret", "secret_idle"))

            AccountAccountGroup.objects.get_or_create(
                account_account=account,
                account_group=default_group,
            )

            activation_url = request.build_absolute_uri(
                reverse("account_activate", kwargs={"token": token})
            )
            message = render_to_string(
                "default/emails/account_activation.txt",
                {
                    "name": account.name,
                    "activation_url": activation_url,
                    "expires_at": expires_at,
                },
            )
            sent = send_mail(
                subject=t("account_activation"),
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            if sent != 1:
                raise smtplib.SMTPException("Activation email was not accepted.")
    except (OSError, smtplib.SMTPException, TimeoutError):
        logger.exception("Failed to send account activation email.")
        return _registration_response(
            request,
            {"success": False, "error": t("text_send_error")},
            status=503,
        )

    return _registration_response(
        request,
        {
            "success": True,
            "message": t("email_activation"),
        },
    )


@require_http_methods(["GET", "POST"])
def account_activate(request, token):
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    if request.method == "GET":
        can_activate = AccountAccount.objects.filter(
            secret=token_hash,
            secret_idle__gt=timezone.now(),
            active=False,
        ).exists()
        return render(
            request,
            "default/pages/account_activation.html",
            {
                "activated": False,
                "can_activate": can_activate,
                "token": token if can_activate else "",
            },
            status=200 if can_activate else 400,
        )

    with transaction.atomic():
        account = (
            AccountAccount.objects
            .select_for_update()
            .filter(
                secret=token_hash,
                secret_idle__gt=timezone.now(),
                active=False,
            )
            .first()
        )
        if account is None:
            return render(
                request,
                "default/pages/account_activation.html",
                {"activated": False, "can_activate": False},
                status=400,
            )

        account.active = True
        account.secret = ""
        account.secret_idle = None
        account.save(update_fields=("active", "secret", "secret_idle"))

    request.session.cycle_key()
    request.session["account_id"] = account.pk
    request.session.set_expiry(0)
    return render(
        request,
        "default/pages/account_activation.html",
        {"activated": True, "can_activate": False},
    )
