# apps/estates/developers/api.py

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import Developer


def developer_detail_api(request, pk):
    dev = get_object_or_404(Developer, pk=pk, is_deleted=False)

    data = {
        "id": dev.id,
        "name": dev.name,
        "logo": dev.logo.url if dev.logo else None,

        "contacts": [
            {
                "type": c.contact_type.code,
                "label": c.contact_type.name,
                "value": c.value,
                "description": c.description,
            }
            for c in dev.developercontacts.all()
        ],

        "departments": [
            {
                "name": d.name,
                "contacts": [
                    {
                        "type": c.contact_type.code,
                        "value": c.value,
                    }
                    for c in d.contacts.all()
                ]
            }
            for d in dev.developerdepartments.all()
        ],
    }

    return JsonResponse(data)