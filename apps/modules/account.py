from collections.abc import Mapping

from apps.accounts.models import AccountAccount
from apps.core.dictionaries.models import ContactType

MODULE = "default/modules/account.html"


def get_account_contacts(account):
    contacts = account.contacts
    if not isinstance(contacts, Mapping):
        return []

    contact_ids = []
    for contact_id in contacts:
        try:
            contact_ids.append(int(contact_id))
        except (TypeError, ValueError):
            continue

    contact_types = ContactType.objects.in_bulk(contact_ids)
    contact_types_by_id = {
        str(contact_id): contact_type
        for contact_id, contact_type in contact_types.items()
    }
    account_contacts = [
        {
            "type": contact_type.name if contact_type else f"Контакт {contact_id}",
            "type_id": int(contact_id),
            "code": contact_type.code if contact_type else "",
            "prefix": contact_type.prefix if contact_type else "",
            "postfix": contact_type.postfix if contact_type else "",
            "value": value,
        }
        for contact_id, value in contacts.items()
        for contact_type in (contact_types_by_id.get(str(contact_id)),)
    ]

    return account_contacts


def get_context(request, module):
    account_id = request.session.get("account_id")
    if not isinstance(account_id, int) or account_id <= 0:
        return {"account": None}

    account = (
        AccountAccount.objects
        .filter(pk=account_id, active=True)
        .prefetch_related("groups")
        .first()
    )
    if account is None:
        return {"account": None}

    return {
        "account": account,
        "account_groups": account.groups.all(),
        "account_contacts": get_account_contacts(account),
        "all_contact_types": list(ContactType.objects.all().order_by("name")),
    }
