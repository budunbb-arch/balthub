# /opt/balthub/apps/maps/models.py

from django.db import models


class MapSettings(models.Model):

    PROVIDER_YANDEX = "yandex"
    PROVIDER_2GIS = "2gis"

    PROVIDERS = [
        (PROVIDER_YANDEX, "Яндекс Карты"),
        (PROVIDER_2GIS, "2GIS"),
    ]

    provider = models.CharField(
        max_length=20,
        choices=PROVIDERS,
        default=PROVIDER_YANDEX,
        verbose_name="Поставщик карт",
    )

    api_key = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="API Key",
    )

    secret_key = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Secret Key",
    )

    language = models.CharField(
        max_length=20,
        default="ru_RU",
        verbose_name="Язык",
    )

    default_zoom = models.PositiveSmallIntegerField(
        default=16,
        verbose_name="Zoom",
    )

    default_height = models.PositiveSmallIntegerField(
        default=450,
        verbose_name="Высота карты",
    )

    show_controls = models.BooleanField(
        default=True,
        verbose_name="Показывать элементы управления",
    )

    clusterize = models.BooleanField(
        default=True,
        verbose_name="Объединять маркеры",
    )

    enabled = models.BooleanField(
        default=True,
        verbose_name="Использовать карты",
    )

    class Meta:
        db_table = "core_mapsettings"
        verbose_name = "Настройки карт"
        verbose_name_plural = "Настройки карт"

    def __str__(self):
        return "Настройки карт"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj