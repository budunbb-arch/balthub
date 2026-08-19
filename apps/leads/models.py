# apps/leads/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.core.documents.models import Document
from apps.core.dictionaries.models import ContactType


HINT_NO_CALL = "no_call"
HINT_NO_VOICE = "no_voice"

HINT_CHOICES = [
    (HINT_NO_CALL, _("Без звонков")),
    (HINT_NO_VOICE, _("Без голосовых сообщений")),
]


class FeedbackModule(models.Model):
    module = models.ForeignKey(
        "core.Module",
        on_delete=models.CASCADE,
        related_name="feedback_modules",
        verbose_name=_("Модуль"),
        null=True,
        blank=True,
    )
    header = models.CharField(max_length=255, verbose_name=_("Заголовок"))
    hint = models.CharField(
        max_length=20,
        choices=HINT_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Подсказка"),
    )
    personal_data = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feedback_personal_data",
        verbose_name=_("Документ обработки персональных данных"),
    )
    policy = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feedback_policy",
        verbose_name=_("Документ политики конфиденциальности"),
    )
    manager_email = models.EmailField(verbose_name=_("Email для отправки"))
    message_tpl = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Шаблон сообщения"),
        help_text=_("Используется как префикс перед комментарием пользователя"),
    )
    contact_types = models.ManyToManyField(
        ContactType,
        blank=True,
        verbose_name=_("Типы контактов"),
        help_text=_("Какие поля контактов показывать в форме"),
    )

    class Meta:
        verbose_name = _("Модуль обратной связи")
        verbose_name_plural = _("Модули обратной связи")
        ordering = ["id"]

    def __str__(self):
        return self.header or str(self.id)


class Lead(models.Model):

    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    name = models.CharField(max_length=255, verbose_name="Имя")
    phone = models.CharField(max_length=100, verbose_name="Телефон")
    email = models.EmailField(max_length=255, verbose_name="Email")
    telegram = models.CharField(max_length=100, blank=True, null=True, verbose_name="Telegram")
    max = models.CharField(max_length=255, blank=True, null=True, verbose_name="MAX")
    message = models.TextField(blank=True, null=True, verbose_name="Сообщение")
    work_at = models.DateTimeField(blank=True, null=True, verbose_name="Дата обработки")
    work_by = models.CharField(max_length=255, blank=True, null=True, verbose_name="Обработал")
    requested_date = models.DateField(blank=True, null=True, verbose_name="Желаемая дата")

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-added_at"]

    def __str__(self):
        return self.name or str(self.id)