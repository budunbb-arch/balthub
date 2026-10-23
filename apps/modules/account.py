from apps.accounts.models import AccountAccount
from apps.core.dictionaries.models import ContactType

MODULE = "default/modules/account.html"


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

    contacts = account.contacts if isinstance(account.contacts, dict) else {}
    contact_ids = []
    for contact_id in contacts:
        try:
            contact_ids.append(int(contact_id))
        except (TypeError, ValueError):
            continue

    contact_types = ContactType.objects.in_bulk(contact_ids)
    contact_names = {
        str(contact_id): contact_type.name
        for contact_id, contact_type in contact_types.items()
    }
    account_contacts = [
        {
            "type": contact_names.get(
                str(contact_id),
                f"Контакт {contact_id}",
            ),
            "value": value,
        }
        for contact_id, value in contacts.items()
    ]
    return {
        "account": account,
        "account_groups": account.groups.all(),
        "account_contacts": account_contacts,
    }
