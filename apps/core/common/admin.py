# apps/core/common/admin.py

from django import forms
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
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


class SoftDeleteAdmin(admin.ModelAdmin):
    """Базовый класс для админок с мягким удалением.
    Автоматически проставляет created_by/edited_by из request.user,
    а также даты *__at при изменении статусов."""

    # Поля, которые исключаем из формы — они проставляются автоматически
    auto_fields = [
        "created_at", "created_by",
        "edited_at", "edited_by",
        "published_at", "published_by",
        "deleted_at", "deleted_by",
        "origin_type", "origin_parser",
        "is_edited",
    ]

    def get_exclude(self, request, obj=None):
        exclude = super().get_exclude(request, obj) or []
        return list(exclude) + self.auto_fields

    def save_model(self, request, obj, form, change):
        now = timezone.now()

        if not change:
            # Создание — проставляем created_by
            obj.created_by = request.user
            obj.origin_type = "manual"

        # Проставляем edited_by при любом сохранении из админки
        obj.edited_by = request.user
        obj.edited_at = now

        # published_at/published_by при is_public
        if obj.is_public and not obj.published_at:
            obj.published_at = now
            obj.published_by = request.user

        # deleted_at/deleted_by при is_deleted + авто-снятие с публикации
        if obj.is_deleted:
            obj.is_public = False
            if not obj.deleted_at:
                obj.deleted_at = now
                obj.deleted_by = request.user

        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

    def delete_queryset(self, request, queryset):
        queryset.soft_delete(request.user)

    def delete_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, object_id)

        if request.method == "POST":
            obj.delete(user=request.user)

            return HttpResponseRedirect(
                reverse(
                    f"admin:{self.opts.app_label}_{self.opts.model_name}_changelist"
                )
            )

        return super().delete_view(request, object_id, extra_context)

    def delete_model(self, request, obj):
        obj.delete(user=request.user)
