from django.test import RequestFactory, TestCase

from apps.accounts.models import AccountAccount, AccountGroup
from apps.core.dictionaries.models import ContactType
from apps.modules.account import get_context


class AccountModuleTests(TestCase):
    def setUp(self):
        self.request = RequestFactory().get("/")
        self.contact_type = ContactType.objects.create(
            name="Email",
            code="email",
        )
        self.account = AccountAccount.objects.create(
            name="Иван Иванов",
            active=True,
            contacts={str(self.contact_type.pk): "ivan@example.com"},
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
            [{"type": "Email", "value": "ivan@example.com"}],
        )

    def test_guest_does_not_receive_account_data(self):
        self.request.session = {}

        self.assertEqual(get_context(self.request, None), {"account": None})

    def test_inactive_account_does_not_receive_profile(self):
        self.account.active = False
        self.account.save(update_fields=("active",))

        self.assertEqual(get_context(self.request, None), {"account": None})
