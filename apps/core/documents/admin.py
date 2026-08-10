# apps/core/documents/admin.py

from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("document_name", "document_date", "document_public", "document_status", "document_comment")
    list_filter = ("document_date", "document_public", "document_status")
    search_fields = ("document_name", "document_comment", "document_content")

    fieldsets = (
        (None, {
            "fields": (
                "document_name",
                "document_content",
                "document_file",
                "document_public",
                "document_status",
                "document_comment",
            )
        }),
    )
