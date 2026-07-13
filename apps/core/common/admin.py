# apps/core/common/admin.py

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from apps.core.models import Module, SiteSettings


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("name", "position", "route", "is_active", "order")
    list_filter = ("position", "is_active")
    search_fields = ("name", "template", "route")
    ordering = ("position", "order")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "site_name",
        "is_disabled",
        "default_title",
        "default_canonical",
        "default_robots",
    )
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

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        qs = self.get_queryset(request)
        obj = qs.first()
        if obj:
            opts = self.model._meta
            return HttpResponseRedirect(
                reverse(
                    "admin:%s_%s_change" % (opts.app_label, opts.model_name),
                    args=(obj.pk,),
                )
            )
        return super().changelist_view(request, extra_context=extra_context)
