# /opt/balthub/apps/core/common/models.py

from django.conf import settings
from django.db import models
from django.utils import timezone


class BaseModel(models.Model):

    # --- Статусы ---
    is_public = models.BooleanField(default=False, db_index=True)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False, db_index=True)

    # --- Даты ---
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # --- Пользователи ---
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created"
    )
    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_edited"
    )
    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_published"
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_deleted"
    )
    origin_type = models.CharField(
        max_length=20,
        choices=[
            ("manual", "Ручной ввод"),
            ("parser", "Парсер"),
            ("api", "API"),
            ("import", "Импорт"),
        ],
        default="manual",
        db_index=True,
        verbose_name="Источник создания",
    )

    origin_parser = models.ForeignKey(
        "core.Parser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_origin",
        verbose_name="Парсер-источник",
    )

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, user=None):
        self.is_deleted = True
        self.is_public = False
        self.deleted_at = timezone.now()

        if user:
            self.deleted_by = user

        self.save(update_fields=[
            "is_deleted",
            "is_public",
            "deleted_at",
            "deleted_by",
        ])


    def hard_delete(self):
        super().delete()


    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=[
            "is_deleted",
            "deleted_at",
            "deleted_by",
        ])


POSITIONS = [
    ("main_menu", "Главное меню"),
    ("account_menu", "Меню аккаунта"),
    ("sidebar", "Сайдбар"),
    ("content_top", "Верх страницы"),
    ("content_bottom", "Низ страницы"),
]

class Module(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название модуля")
    template = models.CharField(max_length=255, verbose_name="Путь к шаблону")
    position = models.CharField(max_length=50, choices=POSITIONS, verbose_name="Позиция")
    route = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="URL или начало URL, где показывать модуль. Пустое = глобальный"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        ordering = ["position", "id"]
        verbose_name = "Модуль"
        verbose_name_plural = "Модули"

    def __str__(self):
        return self.name


