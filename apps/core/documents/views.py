# apps/core/documents/views.py

from django.shortcuts import render, get_object_or_404
from .models import Document


def documents_list(request):
    documents = Document.objects.filter(
        document_public=True,
        document_status="released",
    ).order_by("-document_date", "-id")

    return render(request, "default/pages/documents.html", {
        "documents": documents,
    })


def document_modal(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    return render(request, "default/modules/document_modal.html", {
        "document": document,
    })
