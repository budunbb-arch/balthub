# /opt/balthub/apps/estates/developers/admin.py

from apps.core.common.admin import SoftDeleteAdmin


class DeveloperAdmin(SoftDeleteAdmin):
    list_display = ("name", "is_public", "is_deleted", "created_at")
    search_fields = ("name",)
    list_filter = ("is_public", "is_deleted")
    ordering = ("name",)
