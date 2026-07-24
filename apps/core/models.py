# /opt/balthub/apps/core/models.py

import json
import logging

from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from apps.core.common.models import Module as BaseModule


logger = logging.getLogger(__name__)


class SiteSettings(models.Model):
    site_name = models.CharField(
        max_length=255,
        default="Balthub",
        verbose_name="Название сайта",
    )
    default_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Заголовок по умолчанию",
    )
    default_description = models.TextField(
        blank=True,
        verbose_name="Описание по умолчанию",
    )
    default_keywords = models.TextField(
        blank=True,
        verbose_name="Ключевые слова по умолчанию",
    )
    default_canonical = models.URLField(
        blank=True,
        verbose_name="Канонический URL по умолчанию",
    )
    default_robots = models.CharField(
        max_length=50,
        default="index, follow",
        verbose_name="Robots по умолчанию",
    )
    is_disabled = models.BooleanField(
        default=False,
        verbose_name="Выключить сайт",
        help_text="Показывать заглушку всем пользователям, кроме администраторов.",
    )

    class Meta:
        db_table = "core_sitesettings"
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return "Настройки сайта"

    @classmethod
    def get_solo(cls):
        return cls.objects.first()


class Parser(models.Model):

    ENGINE_NMARKET = "nmarket"

    ENGINE_CHOICES = [
        (ENGINE_NMARKET, "НМаркет"),
    ]

    STATUS_PENDING = "pending"
    STATUS_STARTED = "started"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Ожидает"),
        (STATUS_STARTED, "Выполняется"),
        (STATUS_SUCCESS, "Успешно"),
        (STATUS_FAILED, "Ошибка"),
        (STATUS_CANCELLED, "Отменено")
    ]

    name = models.CharField(max_length=255, verbose_name="Название парсера")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Идентификатор")
    engine = models.CharField(
        max_length=30,
        choices=ENGINE_CHOICES,
        default=ENGINE_NMARKET,
        verbose_name="Движок",
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    source_url = models.URLField(blank=True, verbose_name="URL фида")
    auth_username = models.CharField(max_length=255, blank=True, verbose_name="Имя пользователя")
    auth_password = models.CharField(max_length=255, blank=True, verbose_name="Пароль")
    headers = models.JSONField(blank=True, null=True, verbose_name="Заголовки")
    schedule = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Расписание",
        help_text="Cron-выражение, например 0 3 * * *",
    )
    last_run = models.DateTimeField(null=True, blank=True, verbose_name="Последний запуск")
    last_status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        blank=True,
        verbose_name="Статус последнего запуска",
    )
    last_message = models.TextField(blank=True, verbose_name="Сообщение последнего запуска")
    last_file = models.FileField(
        upload_to="imports/%Y/%m/%d",
        blank=True,
        null=True,
        verbose_name="Последний файл",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")

    class Meta:
        verbose_name = "Парсер"
        verbose_name_plural = "Парсеры"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        self._sync_periodic_task()

    PERIODIC_TASK = "apps.core.tasks.run_parser_task"


    def _sync_periodic_task(self):
        if not self.schedule or not self.is_active:
            self._delete_periodic_task()
            return

        from django_celery_beat.models import (
            CrontabSchedule,
            PeriodicTask,
        )

        try:
            minute, hour, day_of_month, month_of_year, day_of_week = (
                self.schedule.split()
            )

            crontab, _ = CrontabSchedule.objects.get_or_create(
                minute=minute,
                hour=hour,
                day_of_month=day_of_month,
                month_of_year=month_of_year,
                day_of_week=day_of_week,
                timezone="Europe/Amsterdam",   # или UTC
            )

            PeriodicTask.objects.update_or_create(
                name=self.get_periodic_task_name(),
                defaults={
                    "task": self.PERIODIC_TASK,
                    "crontab": crontab,
                    "enabled": self.is_active,
                    "kwargs": json.dumps({
                        "parser_id": self.pk,
                    }),
                },
            )

        except Exception:
            logger.exception(
                "Failed to synchronize PeriodicTask for parser %s",
                self.pk,
            )

    def _delete_periodic_task(self):
        try:
            from django_celery_beat.models import PeriodicTask

            PeriodicTask.objects.filter(name=self.get_periodic_task_name()).delete()
        except Exception:
            pass

    def get_periodic_task_name(self) -> str:
        return f"parser-run-{self.slug or self.pk}"

    def __str__(self):
        return self.name


class ParserRun(models.Model):
    parser = models.ForeignKey(
        Parser,
        on_delete=models.CASCADE,
        related_name="runs",
        verbose_name="Парсер",
    )
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="Запуск начат")
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name="Запуск завершён")
    status = models.CharField(
        max_length=50,
        choices=Parser.STATUS_CHOICES,
        verbose_name="Статус",
    )
    message = models.TextField(blank=True, verbose_name="Сообщение")
    traceback = models.TextField(blank=True, default="", verbose_name="Трассировка ошибки")
    feed_file = models.FileField(
        upload_to="imports/%Y/%m/%d",
        blank=True,
        null=True,
        verbose_name="Файл фида",
    )
    items_processed = models.IntegerField(null=True, blank=True, verbose_name="Обработано записей")

    projects_created = models.PositiveIntegerField(default=0)
    projects_updated = models.PositiveIntegerField(default=0)

    houses_created = models.PositiveIntegerField(default=0)
    houses_updated = models.PositiveIntegerField(default=0)

    flats_created = models.PositiveIntegerField(default=0)
    flats_updated = models.PositiveIntegerField(default=0)

    developers_created = models.PositiveIntegerField(default=0)
    developers_updated = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    cancel_requested = models.BooleanField(
        default=False,
        verbose_name="Запрошена остановка",
    )

    class Meta:
        verbose_name = "Запуск парсера"
        verbose_name_plural = "Запуски парсеров"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.parser.name} - {self.status}"


@receiver(post_delete, sender=Parser)
def delete_parser_periodic_task(sender, instance, **kwargs):
    instance._delete_periodic_task()


class Module(BaseModule):
    class Meta:
        proxy = True
        app_label = "core"
        verbose_name = "Модуль"
        verbose_name_plural = "Модули"
