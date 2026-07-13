from django.contrib import admin
from .models import Developer


class DeveloperAdmin(admin.ModelAdmin):
    list_display = ("name", "is_public", "is_deleted", "created_at")
    search_fields = ("name",)
    list_filter = ("is_public", "is_deleted")
    ordering = ("name",)
