# apps/core/common/admin.py

from django.contrib import admin
from .models import Module
from apps.core.models import SiteSettings

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("name", "position", "route", "is_active", "order")
    list_filter = ("position", "is_active")
    search_fields = ("name", "template", "route")
    ordering = ("position", "order")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "is_disabled", "default_title", "default_canonical", "default_robots")
    fieldsets = (
        (None, {
            "fields": (
                "site_name",
                "is_disabled",
                "default_title",
                "default_description",
                "default_keywords",
                "default_canonical",
                "default_robots",
            )
        }),
    )
