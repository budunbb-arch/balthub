# apps/core/common/admin.py

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.forms.models import construct_instance
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from apps.core.models import Module, SiteSettings
from apps.modules.models import HtmlModule, TagsMenu, ProjectDescriptionSettings
import logging


class RelativeURLModelForm(forms.ModelForm):
    """ModelForm, которая разрешает относительные пути /media/... в URL-полях.

    Django в ModelForm._post_clean() вызывает instance.full_clean(),
    которая запускает валидаторы полей модели, включая URLValidator.
    Здесь мы временно отключаем URLValidator у URL-полей модели,
    потому что валидацию URL уже выполнила форма (RelativeURLField).
    """

    def _post_clean(self):
        opts = self._meta
        exclude = self._get_validation_exclusions()

        # Сохраняем оригинальные валидаторы URL-полей модели,
        # чтобы временно убрать из них URLValidator
        saved_validators = {}
        url_fields = []
        for field in self.instance._meta.fields:
            if isinstance(field, models.URLField):
                url_fields.append(field)
                saved_validators[field] = list(field.validators)
                field.validators = [
                    v for v in field.validators
                    if not isinstance(v, URLValidator)
                ]

        try:
            try:
                self.instance = construct_instance(
                    self, self.instance, opts.fields, opts.exclude
                )
            except ValidationError as e:
                self._update_errors(e)

            try:
                self.instance.full_clean(exclude=exclude, validate_unique=False)
            except ValidationError as e:
                self._update_errors(e)

            # Validate uniqueness if needed.
            if self._validate_unique:
                self.validate_unique()
        finally:
            for field, validators in saved_validators.items():
                field.validators = validators


class RelativeURLField(forms.URLField):
    """Allow both absolute URLs and relative media paths like /media/..."""

    def _is_relative(self, value):
        if not isinstance(value, str):
            return False

        value = value.strip()

        return value.startswith(("/", "media/", "uploads/"))

    def to_python(self, value):
        if value in self.empty_values:
            return value

        value = str(value)
        if self.strip:
            value = value.strip()

        # Относительные пути вида /media/... не должны получать схему http://
        if self._is_relative(value):
            return value

        return super().to_python(value)

    def validate(self, value):
        if value in self.empty_values:
            return

        if self._is_relative(value):
            return

        super().validate(value)

    def run_validators(self, value):
        if value in self.empty_values:
            return

        if self._is_relative(value):
            return

        super().run_validators(value)


class RelativeURLAdminMixin:
    form = RelativeURLModelForm

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if isinstance(db_field, models.URLField):
            kwargs["form_class"] = RelativeURLField
            return db_field.formfield(**kwargs)

        return super().formfield_for_dbfield(db_field, request, **kwargs)


class RelativeURLStackedInline(RelativeURLAdminMixin, admin.StackedInline):
    pass


class RelativeURLTabularInline(RelativeURLAdminMixin, admin.TabularInline):
    pass


@admin.register(HtmlModule)
class HtmlModuleAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code", "content")


from apps.leads.models import FeedbackModule
from apps.modules.models import FooterMenuItem

logger = logging.getLogger(__name__)


class FeedbackModuleInline(admin.StackedInline):
    model = FeedbackModule
    fieldsets = (
        (None, {
            "fields": (
                "header",
                "hint",
                "personal_data",
                "policy",
                "manager_email",
                "message_tpl",
                "contact_types",
            )
        }),
    )
    filter_horizontal = ("contact_types",)
    extra = 1


class FooterMenuItemInline(admin.TabularInline):
    model = FooterMenuItem
    extra = 1
    fields = ("title", "url", "order", "is_active")


class ProjectDescriptionSettingsInline(admin.StackedInline):
    model = ProjectDescriptionSettings
    fieldsets = (
        (None, {
            "fields": (
                "header",
                "header_info",
                "personal_data",
                "policy",
                "message_tpl",
                "message_tpl_info",
                "manager_email",
            )
        }),
    )
    extra = 1


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "position", "route", "html_module", "is_active", "order")
    list_filter = ("position", "is_active", "type")
    search_fields = ("name", "template", "route", "html_module__name", "html_module__code")
    ordering = ("position", "order")
    inlines = [FeedbackModuleInline, FooterMenuItemInline, ProjectDescriptionSettingsInline]

    def get_inline_instances(self, request, obj=None):
        inlines = super().get_inline_instances(request, obj)
        if not obj:
            return []
        if obj.type == "feedback":
            return [i for i in inlines if isinstance(i, FeedbackModuleInline)]
        if obj.template == "default/modules/footer_menu.html":
            return [i for i in inlines if isinstance(i, FooterMenuItemInline)]
        if obj.type == "tags_menu":
            from apps.modules.admin import TagsMenuInline
            return [i for i in inlines if isinstance(i, TagsMenuInline)]
        if obj.type == "project_description":
            return [i for i in inlines if isinstance(i, ProjectDescriptionSettingsInline)]
        return []

    fieldsets = (
        (None, {
            "fields": (
                "name",
                "type",
                "template",
                "position",
                "route",
                "html_module",
                "is_active",
                "order",
            )
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly = []
        if obj and obj.type == "html":
            readonly += ["template", "route"]
        if obj and obj.type == "feedback":
            readonly += ["template"]
        if obj and obj.type == "tags_menu":
            readonly += ["template"]
        return readonly

    def get_exclude(self, request, obj=None):
        exclude = []
        if obj and obj.type == "html":
            exclude += ["template", "route"]
        if obj and obj.type == "feedback":
            exclude += ["template"]
        if obj and obj.type == "tags_menu":
            exclude += ["template"]
        return exclude

    def save_model(self, request, obj, form, change):
        if obj.type == "html" and not obj.template:
            obj.template = "default/modules/html_module.html"
        if obj.type == "feedback" and not obj.template:
            obj.template = "default/modules/feedback.html"
        if obj.type == "footer_menu" and not obj.template:
            obj.template = "default/modules/footer_menu.html"
        if obj.type == "tags_menu" and not obj.template:
            obj.template = "default/modules/tags_menu.html"
        super().save_model(request, obj, form, change)

        if obj.type == "tags_menu":
            TagsMenu.objects.get_or_create(module=obj)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        if obj.type == "feedback":
            logger.info("[FEEDBACK ADMIN] saving related for module_id=%s", obj.pk)
            for fm in obj.feedback_modules.all():
                logger.info("[FEEDBACK ADMIN] existing fm=%s module=%s", fm.pk, fm.module_id)
                if fm.module_id != obj.pk:
                    fm.module = obj
                    fm.save(update_fields=["module"])
            if not obj.feedback_modules.exists():
                created = FeedbackModule.objects.create(module=obj)
                logger.info("[FEEDBACK ADMIN] created fm=%s module=%s", created.pk, obj.pk)


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
        ("Капча Turnstile", {
            "fields": (
                "turnstile_enabled",
                "turnstile_site_key",
                "turnstile_secret_key",
            ),
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


class SoftDeleteAdmin(RelativeURLAdminMixin, admin.ModelAdmin):
    """Базовый класс для админок с мягким удалением.
    Автоматически проставляет created_by/edited_by из request.user,
    а также даты *__at при изменении статусов."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if isinstance(db_field, models.URLField):
            kwargs["form_class"] = RelativeURLField
            return db_field.formfield(**kwargs)

        return super().formfield_for_dbfield(db_field, request, **kwargs)

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
