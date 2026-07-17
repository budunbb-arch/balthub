# /opt/balthub/apps/parsing_section/admin.py

from django.contrib import admin
from django.utils.html import format_html
from apps.core.models import Parser, ParserRun
from apps.core.tasks import run_parser_task

from django.urls import path, reverse
from django.shortcuts import redirect
from django.contrib import messages

from .models import ParserProxy, ParserRunProxy



class ParserRunInline(admin.TabularInline):
    model = ParserRun
    extra = 0
    readonly_fields = (
        "parser",
        "started_at",
        "finished_at",
        "status",

        "items_processed",

        "projects_created",
        "projects_updated",

        "houses_created",
        "houses_updated",

        "flats_created",
        "flats_updated",

        "developers_created",
        "developers_updated",

        "message",
        "feed_file_link",
    )
    fields = (
        "parser",

        (
            "started_at",
            "finished_at",
        ),

        (
            "status",
            "items_processed",
        ),

        (
            "developers_created",
            "developers_updated",
        ),

        (
            "projects_created",
            "projects_updated",
        ),

        (
            "houses_created",
            "houses_updated",
        ),

        (
            "flats_created",
            "flats_updated",
        ),

        "message",

        "feed_file_link",
    )
    can_delete = False
    show_change_link = True

    def feed_file_link(self, obj):
        if obj.feed_file:
            return format_html(
                "<a href='{}'>{}</a>",
                obj.feed_file.url,
                obj.feed_file.name,
            )
        return ""

    feed_file_link.short_description = "Файл фида"


@admin.register(ParserProxy)
class ParserAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "engine",
        "is_active",
        "schedule",
        "last_status",
        "last_run",
    )
    list_filter = ("engine", "is_active", "last_status")
    search_fields = ("name", "source_url")
    readonly_fields = ("last_run", "last_status", "last_message", "last_file_link", "run_now_button")
    fieldsets = (
        (None, {
            "fields": (
                "name",
                "slug",
                "engine",
                "is_active",
                "source_url",
                "auth_username",
                "auth_password",
                "headers",
                "schedule",
            )
        }),
        ("Статус", {
            "fields": (
                "last_run",
                "last_status",
                "last_message",
                "last_file_link",
                "run_now_button",
            )
        }),
    )
    inlines = (ParserRunInline,)
    actions = ("run_parser_now", "enable_parsers", "disable_parsers")

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "<int:parser_id>/run/",
                self.admin_site.admin_view(self.run_parser_view),
                name="parsing_section_parserproxy_run",
            ),
            path(
                "<int:parser_id>/stop/",
                self.admin_site.admin_view(
                    self.stop_parser_view
                ),
                name="parsing_section_parserproxy_stop",
            ),
        ]

        return custom_urls + urls

    def run_now_button(self, obj):

        opts = self.model._meta

        if not obj.pk:
            return "-"

        current = (
            ParserRun.objects
            .filter(status=Parser.STATUS_STARTED)
            .select_related("parser")
            .first()
        )

        if current:

            if current.parser_id == obj.id:
                stop_url = reverse(
                    f"admin:{opts.app_label}_{opts.model_name}_stop",
                    args=[obj.pk],
                )

                return format_html(
                    '''
                    <span style="color:green;font-weight:bold">
                        ⏳ Этот парсер уже выполняется
                    </span>
                    &nbsp;&nbsp;
                    <a class="button"
                    style="background:#ba2121;color:white"
                    href="{}">
                    ■ Остановить
                    </a>
                    ''',
                    stop_url,
                )

            return format_html(
                '<span style="color:#d98400;font-weight:bold">'
                '⛔ Выполняется "{}"'
                '</span>',
                current.parser.name,
            )

        opts = self.model._meta

        url = reverse(
            f"admin:{opts.app_label}_{opts.model_name}_run",
            args=[obj.pk],
        )

        return format_html(
            '<a class="button" href="{}">▶ Запустить сейчас</a>',
            url,
        )

    run_now_button.short_description = ""
    
    def run_parser_view(self, request, parser_id):
        opts = self.model._meta
        parser = Parser.objects.filter(pk=parser_id).first()

        if parser is None:
            self.message_user(
                request,
                "Парсер не найден.",
                level=messages.ERROR,
            )

            return redirect(f"admin:{opts.app_label}_{opts.model_name}_changelist")

        run_parser_task.delay(parser.id)

        self.message_user(
            request,
            f'Парсер "{parser.name}" поставлен в очередь.',
            level=messages.SUCCESS,
        )

        return redirect(
            reverse(f"admin:{opts.app_label}_{opts.model_name}_change", args=[parser.id])
        )
    
    def stop_parser_view(self, request, parser_id):

        run = (
            ParserRun.objects
            .filter(
                parser_id=parser_id,
                status=Parser.STATUS_STARTED,
            )
            .first()
        )

        if run:

            run.cancel_requested = True

            run.save(
                update_fields=[
                    "cancel_requested",
                ]
            )

            self.message_user(
                request,
                "Остановка запрошена.",
                level=messages.WARNING,
            )

        return redirect(
            reverse(
                "admin:parsing_section_parserproxy_change",
                args=[parser_id],
            )
        )

    def last_file_link(self, obj):
        if obj.last_file:
            return format_html("<a href='{}'>{}</a>", obj.last_file.url, obj.last_file.name)
        return ""

    last_file_link.short_description = "Последний файл"

    def run_parser_now(self, request, queryset):
        for parser in queryset:
            run_parser_task.delay(parser.id)
        self.message_user(request, "Запуск парсеров поставлен в очередь.")

    run_parser_now.short_description = "Запустить выбранные парсеры сейчас"

    def enable_parsers(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Парсеры включены.")

    enable_parsers.short_description = "Включить выбранные парсеры"

    def disable_parsers(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Парсеры выключены.")

    disable_parsers.short_description = "Выключить выбранные парсеры"



@admin.register(ParserRunProxy)
class ParserRunAdmin(admin.ModelAdmin):

    readonly_fields = (
        "parser",

        "started_at",
        "finished_at",

        "status",

        "items_processed",

        "developers_created",
        "developers_updated",

        "projects_created",
        "projects_updated",

        "houses_created",
        "houses_updated",

        "flats_created",
        "flats_updated",

        "message",

        "feed_file_link",

        "traceback_pre",
    )

    fields = (
        "parser",
        "started_at",
        "finished_at",
        "status",
        "items_processed",
        "developers_created",
        "developers_updated",

        "projects_created",
        "projects_updated",

        "houses_created",
        "houses_updated",

        "flats_created",
        "flats_updated",
        "message",
        "feed_file_link",
        "traceback_pre",
    )

    def traceback_pre(self, obj):
        return format_html(
            "<pre style='white-space:pre-wrap'>{}</pre>",
            obj.traceback,
        )

    traceback_pre.short_description = "Traceback"

    def feed_file_link(self, obj):
        if obj.feed_file:
            return format_html("<a href='{}'>{}</a>", obj.feed_file.url, obj.feed_file.name)
        return ""

    feed_file_link.short_description = "Файл фида"

    def has_add_permission(self, request):
        return False