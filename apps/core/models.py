from django.db import models


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
