from collections import UserDict
from types import SimpleNamespace
from unittest.mock import patch

from django.test import RequestFactory, TestCase

from apps.accounts.models import AccountAccount, AccountGroup
from apps.core.dictionaries.models import ContactType
from apps.core.common.admin import ModuleAdminForm
from apps.core.common.models import Module
from apps.modules.account import get_account_contacts, get_context
from apps.modules.registry import MODULE_HANDLERS, get_module_handler


class AccountModuleTests(TestCase):
    def setUp(self):
        self.request = RequestFactory().get("/")
        self.contact_type = ContactType.objects.create(
            name="Email",
            code="fa-regular fa-envelope",
            prefix="mailto:",
        )
        self.phone_type = ContactType.objects.create(
            name="Телефон",
            code="fa-solid fa-phone",
            prefix="+",
            postfix=" добавочный",
        )
        self.account = AccountAccount.objects.create(
            name="Иван Иванов",
            active=True,
            contacts={
                str(self.contact_type.pk): "ivan@example.com",
                str(self.phone_type.pk): "+7 900 000-00-00",
            },
        )
        self.group = AccountGroup.objects.create(name="Клиенты")
        self.account.groups.add(self.group)
        self.request.session = {"account_id": self.account.pk}

    def test_returns_active_account_profile(self):
        data = get_context(self.request, None)

        self.assertEqual(data["account"], self.account)
        self.assertEqual(list(data["account_groups"]), [self.group])
        self.assertEqual(
            data["account_contacts"],
            [
                {
                    "type": "Email",
                    "code": "fa-regular fa-envelope",
                    "prefix": "mailto:",
                    "postfix": None,
                    "value": "ivan@example.com",
                },
                {
                    "type": "Телефон",
                    "code": "fa-solid fa-phone",
                    "prefix": "+",
                    "postfix": " добавочный",
                    "value": "+7 900 000-00-00",
                },
            ],
        )

    def test_guest_does_not_receive_account_data(self):
        self.request.session = {}

        self.assertEqual(get_context(self.request, None), {"account": None})


class ModuleHandlerLookupTests(TestCase):
    def test_custom_theme_widget_uses_handler_for_matching_module(self):
        handler = object()
        with patch.dict(
            MODULE_HANDLERS,
            {"default/modules/main_menu.html": handler},
        ):
            self.assertIs(
                get_module_handler("Lx2-style/widgets/main_menu.html"),
                handler,
            )

    def test_custom_non_module_template_has_no_default_handler(self):
        self.assertIsNone(get_module_handler("Lx2-style/widgets/custom_widget.html"))

    def test_module_admin_preserves_selected_template_path(self):
        form = ModuleAdminForm(data={
            "name": "Главное меню",
            "type": "main_menu",
            "template": "Lx2-style/modules/main_menu.html",
            "position": "main_menu",
            "route": "",
            "html_module": "",
            "is_active": "on",
            "order": "0",
        })

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            form.cleaned_data["template"],
            "Lx2-style/modules/main_menu.html",
        )

    def test_contacts_support_mapping_objects(self):
        contacts = UserDict({
            str(self.contact_type.pk): "ivan@example.com",
        })

        self.assertEqual(
            get_account_contacts(SimpleNamespace(contacts=contacts)),
            [
                {
                    "type": "Email",
                    "code": "fa-regular fa-envelope",
                    "prefix": "mailto:",
                    "postfix": None,
                    "value": "ivan@example.com",
                },
            ],
        )

    def test_inactive_account_does_not_receive_profile(self):
        self.account.active = False
        self.account.save(update_fields=("active",))

        self.assertEqual(get_context(self.request, None), {"account": None})
