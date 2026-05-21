from django.conf import settings
from django.db import models


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

    class Meta:
        abstract = True


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
