# /opt/balthub/apps/estates/developers/admin.py

from django.contrib import admin
from django.utils.html import format_html

from apps.core.common.admin import SoftDeleteAdmin
from .models import DeveloperDescription


class DeveloperDescriptionInline(admin.StackedInline):
    model = DeveloperDescription
    extra = 0
    max_num = 1
    fields = ("text_description",)


class DeveloperAdmin(SoftDeleteAdmin):
    class Media:
            css = {
                'all': ('admin/css/developers.css',)
            }

    list_display = ("name", "logo_thumb", "is_public", "is_deleted", "created_at")
    search_fields = ("name",)
    list_filter = ("is_public", "is_deleted")
    ordering = ("name",)
    inlines = (DeveloperDescriptionInline,)

    def logo_thumb(self, obj):
        if not obj.logo:
            return "-"
        return format_html(
            '<img src="{}" class="table-thumb" />',
            obj.logo.url,
        )
    logo_thumb.short_description = "Logo"
