# apps/estates/tags/admin.py

import json

from django import forms
from django.contrib import admin
from django.forms import formset_factory
from django.utils.html import format_html
from django.views.decorators.http import require_POST
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages

from .models import Tag, ProjectTag, FlatTag, AutoTagTask
from .runner import run_autotags


FLAT_PARAM_CHOICES = [
    ("rooms", "Комнаты"),
    ("square", "Площадь"),
    ("floor", "Этаж"),
    ("finish_type", "Отделка"),
    ("balcony_type", "Балкон"),
    ("bathroom_unit_type", "Санузел"),
    ("ceiling_height", "Высота потолков"),
    ("living_square", "Жилая площадь"),
    ("kitchen_square", "Кухня"),
    ("haggle", "Торг"),
    ("mortgage", "Ипотека"),
]

PROJECT_PARAM_CHOICES = [
    ("city", "Город"),
    ("district", "Район"),
    ("property_type", "Тип недвижимости"),
    ("property_category", "Категория"),
]


class TriggerForm(forms.Form):
    param = forms.ChoiceField(choices=[], label="Параметр")
    value = forms.CharField(max_length=255, label="Значение", required=False)


class AutoTagTaskForm(forms.ModelForm):
    object_type = forms.ChoiceField(
        choices=AutoTagTask.OBJECT_TYPE_CHOICES,
        label="Тип объекта",
    )
    autostart = forms.BooleanField(label="Автостарт", required=False)

    class Meta:
        model = AutoTagTask
        fields = ["tag", "object_type", "autostart"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        object_type = None
        if instance and instance.pk:
            object_type = instance.object_type
        elif "data" in kwargs:
            object_type = kwargs["data"].get("object_type")
        
        if object_type == AutoTagTask.OBJECT_TYPE_FLAT:
            choices = FLAT_PARAM_CHOICES
        elif object_type == AutoTagTask.OBJECT_TYPE_PROJECT:
            choices = PROJECT_PARAM_CHOICES
        else:
            choices = []
        
        # We'll handle triggers dynamically in the template


class ProjectTagInline(admin.TabularInline):
    model = ProjectTag
    extra = 1


class FlatTagInline(admin.TabularInline):
    model = FlatTag
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ["name"]}
    inlines = [ProjectTagInline, FlatTagInline]


@admin.register(AutoTagTask)
class AutoTagTaskAdmin(admin.ModelAdmin):
    form = AutoTagTaskForm
    list_display = ("tag", "object_type", "autostart", "id", "run_button")
    list_filter = ("object_type", "autostart")
    search_fields = ("tag__name",)
    ordering = ["id"]
    change_form_template = "admin/estates/tags/autotagtask_change_form.html"
    change_list_template = "admin/estates/tags/autotagtask_changelist.html"

    def object_type_display(self, obj):
        if not obj.object_type:
            return "-"
        return ", ".join(obj.object_type)
    object_type_display.short_description = "Тип объекта"

    def id_display(self, obj):
        return obj.pk
    id_display.short_description = "ID"
    id_display.admin_order_field = "id"

    def render_change_form(self, request, context, *args, **kwargs):
        obj = context.get("original")
        triggers = []
        triggers_json = "[]"
        object_type = ""
        if obj and obj.pk:
            triggers = obj.triggers or []
            triggers_json = json.dumps(triggers)
            object_type = obj.object_type or ""
        context["triggers_data"] = triggers
        context["triggers_json"] = triggers_json
        context["flat_params"] = FLAT_PARAM_CHOICES
        context["project_params"] = PROJECT_PARAM_CHOICES
        context["flat_params_json"] = json.dumps(FLAT_PARAM_CHOICES, ensure_ascii=False)
        context["project_params_json"] = json.dumps(PROJECT_PARAM_CHOICES, ensure_ascii=False)
        context["object_type"] = object_type
        return super().render_change_form(request, context, *args, **kwargs)

    def save_model(self, request, obj, form, change):
        triggers_raw = request.POST.get("triggers_json", "[]")
        try:
            obj.triggers = json.loads(triggers_raw)
        except (json.JSONDecodeError, TypeError):
            obj.triggers = []
        obj.object_type = request.POST.get("object_type", "")
        super().save_model(request, obj, form, change)

    def run_button(self, obj):
        return format_html(
            '<a class="button" href="{}">Запустить</a>',
            f"run/{obj.pk}/",
        )
    run_button.short_description = "Действие"
    run_button.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path("run/<int:pk>/", self.admin_site.admin_view(self.run_view), name="tags_autotagtask_run"),
            path("run-autostart/", self.admin_site.admin_view(self.run_autostart_view), name="tags_autotagtask_run_autostart"),
        ]
        return custom + urls

    def run_view(self, request, pk):
        task = AutoTagTask.objects.get(pk=pk)
        summary = run_autotags(task_id=pk)
        self.message_user(
            request,
            f"Автотег запущен: проверено {summary['objects_checked']} объектов, "
            f"создано {summary['tags_created']} тегов, пропущено {summary['skipped']}.",
            messages.SUCCESS,
        )
        return redirect("admin:tags_autotagtask_changelist")

    def run_autostart_view(self, request):
        tasks = AutoTagTask.objects.filter(autostart=True)
        total_objects_checked = 0
        total_tags_created = 0
        total_skipped = 0
        for task in tasks:
            summary = run_autotags(task_id=task.pk)
            total_objects_checked += summary["objects_checked"]
            total_tags_created += summary["tags_created"]
            total_skipped += summary["skipped"]
        self.message_user(
            request,
            f"Автостарт выполнен: заданий {tasks.count()}, проверено {total_objects_checked} объектов, "
            f"создано {total_tags_created} тегов, пропущено {total_skipped}.",
            messages.SUCCESS,
        )
        return redirect("admin:tags_autotagtask_changelist")
