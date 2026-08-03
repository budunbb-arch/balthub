# /opt/balthub/apps/estates/developers/admin.py

from django.contrib import admin

from apps.core.common.admin import SoftDeleteAdmin
from .models import DeveloperDescription


class DeveloperDescriptionInline(admin.StackedInline):
    model = DeveloperDescription
    extra = 0
    max_num = 1
    fields = ("text_description",)


class DeveloperAdmin(SoftDeleteAdmin):
    list_display = ("name", "is_public", "is_deleted", "created_at")
    search_fields = ("name",)
    list_filter = ("is_public", "is_deleted")
    ordering = ("name",)
    inlines = (DeveloperDescriptionInline,)
