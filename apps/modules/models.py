# /opt/balthub/apps/modules/models.py

from django.db import models


class HtmlModule(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Идентификатор")
    code = models.TextField(verbose_name="HTML содержимое")

    class Meta:
        verbose_name = "HTML модуль"
        verbose_name_plural = "HTML модули"

    def __str__(self):
        return self.name
