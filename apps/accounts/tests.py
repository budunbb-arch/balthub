import hashlib
from datetime import timedelta
from unittest.mock import patch

from django.db import IntegrityError, transaction
from django.contrib import admin
from django.contrib.auth.hashers import check_password, make_password
from django.test import RequestFactory, TestCase
from django.utils import timezone
from django.urls import reverse

from apps.core.dictionaries.models import ContactType

from .models import AccountAccount, AccountAccountGroup, AccountGroup
from .views import (
    account_activate,
    account_dashboard,
    account_password_reset,
    account_password_reset_request,
    account_register,
)


class AccountGroupTests(TestCase):
    def test_group_uses_account_groups_table_and_defaults_flags_to_false(self):
        group = AccountGroup.objects.create(name="Клиенты")

        self.assertEqual(AccountGroup._meta.db_table, "account_groups")
        self.assertFalse(group.employee)
        self.assertFalse(group.client)
        self.assertFalse(group.developer_contact)
        self.assertFalse(group.blog_author)
        self.assertFalse(group.blog_editor)
        self.assertFalse(group.upload_files)
        self.assertEqual(str(group), "Клиенты")

    def test_group_is_registered_in_admin(self):
        self.assertIsInstance(admin.site._registry[AccountGroup], admin.ModelAdmin)


class AccountAccountTests(TestCase):
    def setUp(self):
        self.email_type = ContactType.objects.create(
            name="Электронная почта",
            code="fa-envelope",
        )
        self.account = AccountAccount.objects.create(
            name="Иван",
            secret="hashed-activation-secret",
            contacts={str(self.email_type.pk): "ivan@example.com"},
        )
        self.group = AccountGroup.objects.create(name="Клиенты")

    def test_account_uses_expected_table_and_defaults_inactive(self):
        self.assertEqual(AccountAccount._meta.db_table, "account_account")
        self.assertEqual(self.account.password, "")
        self.assertFalse(self.account.active)
        self.assertEqual(
            self.account.contacts,
            {str(self.email_type.pk): "ivan@example.com"},
        )
        self.assertIsNone(self.account.secret_idle)
        self.assertEqual(str(self.account), "Иван")

    def test_account_can_belong_to_multiple_groups(self):
        other_group = AccountGroup.objects.create(name="Авторы")

        AccountAccountGroup.objects.create(
            account_account=self.account,
            account_group=self.group,
        )
        AccountAccountGroup.objects.create(
            account_account=self.account,
            account_group=other_group,
        )

        self.assertEqual(self.account.groups.count(), 2)
        self.assertEqual(
            AccountAccountGroup._meta.db_table,
            "account_account_groups",
        )

    def test_account_groups_are_registered_in_admin(self):
        self.assertIsInstance(admin.site._registry[AccountAccount], admin.ModelAdmin)
        self.assertIn("password", admin.site._registry[AccountAccount].exclude)

    def test_account_group_pair_must_be_unique(self):
        AccountAccountGroup.objects.create(
            account_account=self.account,
            account_group=self.group,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                AccountAccountGroup.objects.create(
                    account_account=self.account,
                    account_group=self.group,
                )


class AccountRegistrationTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.email_type = ContactType.objects.create(
            name="email",
            code="fa-envelope",
        )
        self.default_group = AccountGroup.objects.create(
            pk=1,
            name="Пользователь",
        )

    def test_registration_creates_inactive_account_with_hashed_password_and_group(self):
        request = self.factory.post(
            "/account/register/",
            {
                "name": "Иван Иванов",
                "email": "ivan@example.com",
                "password": "Unique-password-9281",
                "password_confirm": "Unique-password-9281",
                "captcha_id": "valid-challenge",
                "captcha_value": "42",
            },
        )
        request.session = {}

        with (
            patch("apps.accounts.views.verify_challenge", return_value=True),
            patch("apps.accounts.views.is_turnstile_enabled", return_value=False),
            patch(
                "apps.accounts.views.create_challenge",
                return_value={"id": "new-challenge", "target": 42},
            ),
            patch("apps.accounts.views.send_mail", return_value=1) as send_mail,
        ):
            response = account_register(request)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(send_mail.call_args.kwargs["recipient_list"], ["ivan@example.com"])

        account = AccountAccount.objects.get(name="Иван Иванов")
        self.assertFalse(account.active)
        self.assertTrue(check_password("Unique-password-9281", account.password))
        self.assertNotEqual(account.password, "Unique-password-9281")
        self.assertEqual(
            account.contacts,
            {str(self.email_type.pk): "ivan@example.com"},
        )
        self.assertEqual(list(account.groups.all()), [self.default_group])
        self.assertTrue(account.secret)
        self.assertGreater(account.secret_idle, timezone.now())

    def test_registration_rejects_email_if_any_matching_account_is_active(self):
        AccountAccount.objects.create(
            name="Неактивированный дубль",
            active=False,
            contacts={str(self.email_type.pk): "ivan@example.com"},
        )
        AccountAccount.objects.create(
            name="Иван Иванов",
            active=True,
            contacts={str(self.email_type.pk): "ivan@example.com"},
        )
        request = self.factory.post(
            reverse("account_register"),
            {
                "name": "Другой Пользователь",
                "email": "IVAN@example.com",
                "password": "Unique-password-9281",
                "password_confirm": "Unique-password-9281",
                "captcha_id": "valid-challenge",
                "captcha_value": "42",
            },
        )
        request.session = {}

        with (
            patch("apps.accounts.views.verify_challenge", return_value=True),
            patch(
                "apps.accounts.views.create_challenge",
                return_value={"id": "new-challenge", "target": 42},
            ),
            patch(
                "apps.accounts.views.t",
                side_effect=lambda key: {
                    "text_email_variant0": "email",
                    "text_email_variant1": "e-mail",
                    "text_email_variant2": "электронная почта",
                    "text_email_variant3": "почта",
                    "email_already_registered": "email_already_registered",
                }.get(key, key),
            ),
            patch("apps.accounts.views.send_mail") as send_mail,
        ):
            response = account_register(request)

        self.assertEqual(response.status_code, 409)
        self.assertFalse(response.json()["success"])
        self.assertIn("email_already_registered", response.json()["error"])
        self.assertEqual(AccountAccount.objects.count(), 2)
        send_mail.assert_not_called()

    def test_registration_resends_activation_for_existing_inactive_account(self):
        account = AccountAccount.objects.create(
            name="Иван Иванов",
            active=False,
            secret="old-token-hash",
            secret_idle=timezone.now() - timedelta(minutes=1),
            contacts={str(self.email_type.pk): "ivan@example.com"},
        )
        request = self.factory.post(
            reverse("account_register"),
            {
                "name": "Иван Иванов",
                "email": "ivan@example.com",
                "password": "Unique-password-9281",
                "password_confirm": "Unique-password-9281",
                "captcha_id": "valid-challenge",
                "captcha_value": "42",
            },
        )
        request.session = {}

        with (
            patch("apps.accounts.views.verify_challenge", return_value=True),
            patch(
                "apps.accounts.views.create_challenge",
                return_value={"id": "new-challenge", "target": 42},
            ),
            patch(
                "apps.accounts.views.t",
                side_effect=lambda key: {
                    "text_email_variant0": "email",
                    "text_email_variant1": "e-mail",
                    "text_email_variant2": "электронная почта",
                    "text_email_variant3": "почта",
                    "account_activation": "Активация аккаунта",
                    "email_activation": "Проверьте почту для активации.",
                }.get(key, key),
            ),
            patch(
                "apps.accounts.views.render_to_string",
                return_value="activation message",
            ) as render_email,
            patch("apps.accounts.views.send_mail", return_value=1) as send_mail,
        ):
            response = account_register(request)

        account.refresh_from_db()
        activation_url = render_email.call_args.args[1]["activation_url"]
        token = activation_url.rstrip("/").split("/")[-1]
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(send_mail.call_args.kwargs["recipient_list"], ["ivan@example.com"])
        self.assertEqual(AccountAccount.objects.count(), 1)
        self.assertFalse(account.active)
        self.assertNotEqual(account.secret, "old-token-hash")
        self.assertEqual(
            account.secret,
            hashlib.sha256(token.encode("utf-8")).hexdigest(),
        )
        self.assertGreater(account.secret_idle, timezone.now())

    def test_registration_rejects_name_with_only_one_word(self):
        request = self.factory.post(
            reverse("account_register"),
            {
                "name": "Иван",
                "email": "ivan@example.com",
                "password": "Unique-password-9281",
                "password_confirm": "Unique-password-9281",
                "captcha_id": "valid-challenge",
                "captcha_value": "42",
            },
        )
        request.session = {}

        with (
            patch("apps.accounts.views.verify_challenge", return_value=True),
            patch(
                "apps.accounts.views.create_challenge",
                return_value={"id": "new-challenge", "target": 42},
            ),
        ):
            response = account_register(request)

        self.assertEqual(response.status_code, 400)
        self.assertIn("не менее двух слов", response.json()["error"])
        self.assertFalse(AccountAccount.objects.exists())

    def test_registration_rejects_password_without_required_character_classes(self):
        for password in ("lowercase123", "UPPERCASE123", "NoDigitsHere"):
            with self.subTest(password=password):
                request = self.factory.post(
                    reverse("account_register"),
                    {
                        "name": "Иван Иванов",
                        "email": "ivan@example.com",
                        "password": password,
                        "password_confirm": password,
                        "captcha_id": "valid-challenge",
                        "captcha_value": "42",
                    },
                )
                request.session = {}

                with (
                    patch("apps.accounts.views.verify_challenge", return_value=True),
                    patch(
                        "apps.accounts.views.create_challenge",
                        return_value={"id": "new-challenge", "target": 42},
                    ),
                ):
                    response = account_register(request)

                self.assertEqual(response.status_code, 400)
                self.assertIn("заглавные и строчные буквы и цифры", response.json()["error"])
                self.assertFalse(AccountAccount.objects.exists())

    def test_activation_consumes_valid_token_and_activates_account(self):
        token = "activation-token-for-test"
        account = AccountAccount.objects.create(
            name="Иван Иванов",
            secret=hashlib.sha256(token.encode("utf-8")).hexdigest(),
            secret_idle=timezone.now() + timedelta(hours=1),
            active=False,
        )
        request = self.factory.post(f"/account/activate/{token}/")
        request.session = self.client.session

        with patch("apps.accounts.views.render") as render:
            response = account_activate(request, token)

        account.refresh_from_db()
        self.assertTrue(account.active)
        self.assertEqual(account.secret, "")
        self.assertIsNone(account.secret_idle)
        self.assertEqual(request.session["account_id"], account.pk)
        self.assertEqual(request.session.get_expiry_age(), 0)
        self.assertEqual(
            render.call_args.args[2],
            {"activated": True, "can_activate": False},
        )
        self.assertEqual(response, render.return_value)

    def test_activation_link_get_does_not_activate_or_log_in(self):
        token = "activation-token-for-test"
        account = AccountAccount.objects.create(
            name="Иван Иванов",
            secret=hashlib.sha256(token.encode("utf-8")).hexdigest(),
            secret_idle=timezone.now() + timedelta(hours=1),
            active=False,
        )
        request = self.factory.get(f"/account/activate/{token}/")
        request.session = self.client.session

        with patch("apps.accounts.views.render") as render:
            response = account_activate(request, token)

        account.refresh_from_db()
        self.assertEqual(response, render.return_value)
        self.assertFalse(account.active)
        self.assertNotIn("account_id", request.session)
        self.assertEqual(
            render.call_args.args[2],
            {"activated": False, "can_activate": True, "token": token},
        )

    def test_login_sets_account_session_and_rotates_session_key(self):
        account = AccountAccount.objects.create(
            name="Иван Иванов",
            password=make_password("Unique-password-9281"),
            active=True,
            contacts={str(self.email_type.pk): "ivan@example.com"},
        )
        session = self.client.session
        session["before_login"] = "preserved"
        session.save()
        old_session_key = session.session_key

        with (
            patch("apps.accounts.views.verify_challenge", return_value=True),
            patch("apps.accounts.views.is_turnstile_enabled", return_value=False),
            patch(
                "apps.accounts.views.create_challenge",
                return_value={"id": "new-challenge", "target": 42},
            ),
        ):
            response = self.client.post(
                reverse("account_login"),
                {
                    "email": "IVAN@example.com",
                    "password": "Unique-password-9281",
                    "captcha_id": "valid-challenge",
                    "captcha_value": "42",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(response.json()["next_url"], reverse("account_dashboard"))
        self.assertEqual(self.client.session["account_id"], account.pk)
        self.assertEqual(self.client.session["before_login"], "preserved")
        self.assertNotEqual(self.client.session.session_key, old_session_key)

    def test_login_rejects_inactive_account_without_creating_account_session(self):
        AccountAccount.objects.create(
            name="Иван Иванов",
            password=make_password("Unique-password-9281"),
            active=False,
            contacts={str(self.email_type.pk): "ivan@example.com"},
        )

        with (
            patch("apps.accounts.views.verify_challenge", return_value=True),
            patch("apps.accounts.views.is_turnstile_enabled", return_value=False),
            patch(
                "apps.accounts.views.create_challenge",
                return_value={"id": "new-challenge", "target": 42},
            ),
        ):
            response = self.client.post(
                reverse("account_login"),
                {
                    "email": "ivan@example.com",
                    "password": "Unique-password-9281",
                    "captcha_id": "valid-challenge",
                    "captcha_value": "42",
                },
            )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
        self.assertNotIn("account_id", self.client.session)

    def test_login_rejects_invalid_slider_captcha(self):
        with (
            patch("apps.accounts.views.verify_challenge", return_value=False),
            patch(
                "apps.accounts.views.create_challenge",
                return_value={"id": "new-challenge", "target": 42},
            ),
        ):
            response = self.client.post(
                reverse("account_login"),
                {
                    "email": "ivan@example.com",
                    "password": "Unique-password-9281",
                    "captcha_id": "invalid-challenge",
                    "captcha_value": "42",
                },
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"],
            "Пройдите проверку ползунком.",
        )
        self.assertNotIn("account_id", self.client.session)

    def test_logout_flushes_account_session(self):
        session = self.client.session
        session["account_id"] = 123
        session.save()

        response = self.client.post(reverse("account_logout"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))
        self.assertNotIn("account_id", self.client.session)

    def test_account_dashboard_redirects_without_a_valid_session(self):
        request = self.factory.get("/account/")
        request.session = {}

        response = account_dashboard(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))

    def test_password_reset_request_sends_hashed_one_time_token(self):
        account = AccountAccount.objects.create(
            name="Иван Иванов",
            active=True,
            contacts={str(self.email_type.pk): "ivan@example.com"},
        )
        request = self.factory.post(
            reverse("account_password_reset_request"),
            {
                "email": "ivan@example.com",
                "captcha_id": "valid-challenge",
                "captcha_value": "42",
            },
        )
        request.session = {}

        with (
            patch("apps.accounts.views.verify_challenge", return_value=True),
            patch("apps.accounts.views.is_turnstile_enabled", return_value=False),
            patch(
                "apps.accounts.views.create_challenge",
                return_value={"id": "new-challenge", "target": 42},
            ),
            patch(
                "apps.accounts.views.render_to_string",
                return_value="reset email",
            ) as render_email,
            patch("apps.accounts.views.send_mail", return_value=1) as send_mail,
        ):
            response = account_password_reset_request(request)

        account.refresh_from_db()
        reset_url = render_email.call_args.args[1]["reset_url"]
        token = reset_url.rstrip("/").split("/")[-1]
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertEqual(send_mail.call_args.kwargs["recipient_list"], ["ivan@example.com"])
        self.assertNotEqual(account.secret, token)
        self.assertEqual(
            account.secret,
            hashlib.sha256(token.encode("utf-8")).hexdigest(),
        )
        self.assertGreater(account.secret_idle, timezone.now())

    def test_password_reset_request_has_same_response_for_unknown_email(self):
        request = self.factory.post(
            reverse("account_password_reset_request"),
            {
                "email": "unknown@example.com",
                "captcha_id": "valid-challenge",
                "captcha_value": "42",
            },
        )
        request.session = {}

        with (
            patch("apps.accounts.views.verify_challenge", return_value=True),
            patch(
                "apps.accounts.views.create_challenge",
                return_value={"id": "new-challenge", "target": 42},
            ),
            patch("apps.accounts.views.send_mail") as send_mail,
        ):
            response = account_password_reset_request(request)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertIn("Если активный аккаунт", response.json()["message"])
        send_mail.assert_not_called()

    def test_password_reset_changes_password_and_consumes_token(self):
        token = "password-reset-token"
        account = AccountAccount.objects.create(
            name="Иван Иванов",
            password=make_password("Old-unique-password-3841"),
            active=True,
            secret=hashlib.sha256(token.encode("utf-8")).hexdigest(),
            secret_idle=timezone.now() + timedelta(hours=1),
        )
        request = self.factory.post(
            reverse("account_password_reset", kwargs={"token": token}),
            {
                "password": "New-unique-password-9274",
                "password_confirm": "New-unique-password-9274",
            },
        )
        request.session = {}

        with patch("apps.accounts.views.render") as render:
            response = account_password_reset(request, token)

        account.refresh_from_db()
        self.assertEqual(response, render.return_value)
        self.assertTrue(check_password("New-unique-password-9274", account.password))
        self.assertFalse(check_password("Old-unique-password-3841", account.password))
        self.assertEqual(account.secret, "")
        self.assertIsNone(account.secret_idle)
        self.assertEqual(
            render.call_args.args[2],
            {"completed": True, "can_reset": False},
        )

    def test_password_reset_get_does_not_consume_valid_token(self):
        token = "password-reset-token"
        account = AccountAccount.objects.create(
            name="Иван Иванов",
            active=True,
            secret=hashlib.sha256(token.encode("utf-8")).hexdigest(),
            secret_idle=timezone.now() + timedelta(hours=1),
        )
        request = self.factory.get(
            reverse("account_password_reset", kwargs={"token": token})
        )

        with patch("apps.accounts.views.render") as render:
            response = account_password_reset(request, token)

        account.refresh_from_db()
        self.assertEqual(response, render.return_value)
        self.assertTrue(account.secret)
        self.assertIsNotNone(account.secret_idle)
        self.assertEqual(
            render.call_args.args[2],
            {"can_reset": True, "token": token},
        )
