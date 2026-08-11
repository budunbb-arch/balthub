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


class FooterMenuItem(models.Model):
    module = models.ForeignKey(
        "core.Module",
        on_delete=models.CASCADE,
        related_name="footer_menu_items",
        verbose_name="Модуль",
    )
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    url = models.CharField(max_length=255, verbose_name="URL")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Пункт меню футера"
        verbose_name_plural = "Пункты меню футера"

    def __str__(self):
        return self.title


class TagsMenu(models.Model):
    module = models.OneToOneField(
        "core.Module",
        on_delete=models.CASCADE,
        related_name="tags_menu",
        verbose_name="Модуль",
    )
    title = models.CharField(max_length=255, verbose_name="Заголовок меню")

    class Meta:
        verbose_name = "Меню тегов"
        verbose_name_plural = "Меню тегов"
        ordering = ["id"]

    def __str__(self):
        return self.title


class TagsMenuItem(models.Model):
    tags_menu = models.ForeignKey(
        TagsMenu,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Меню тегов",
    )
    tag = models.ForeignKey(
        "tags.Tag",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name="Тег",
    )
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Пункт меню тегов"
        verbose_name_plural = "Пункты меню тегов"

    def __str__(self):
        return str(self.tag)
