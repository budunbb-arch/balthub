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


class ProjectDescriptionSettings(models.Model):
    module = models.OneToOneField(
        "core.Module",
        on_delete=models.CASCADE,
        related_name="project_description_settings",
        verbose_name="Модуль",
    )
    header = models.CharField(max_length=255, verbose_name="Заголовок формы")
    personal_data = models.ForeignKey(
        "documents.Document",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_description_personal_data",
        verbose_name="Обработка персональных данных",
    )
    policy = models.ForeignKey(
        "documents.Document",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_description_policy",
        verbose_name="Политика конфиденциальности",
    )
    message_tpl = models.TextField(
        blank=True,
        null=True,
        verbose_name="Шаблон сообщения",
        help_text="Префикс перед комментарием пользователя",
    )
    manager_email = models.EmailField(blank=True, null=True, verbose_name="Email для отправки")
    header_info = models.CharField(max_length=255, blank=True, null=True, verbose_name="Заголовок для 'Узнать подробнее'")
    message_tpl_info = models.TextField(blank=True, null=True, verbose_name="Шаблон сообщения для 'Узнать подробнее'")

    class Meta:
        verbose_name = "Настройки описания проекта"
        verbose_name_plural = "Настройки описания проекта"

    def __str__(self):
        return f"Настройки {self.module.name}"


class TagCollection(models.Model):
    module = models.OneToOneField(
        "core.Module",
        on_delete=models.CASCADE,
        related_name="tag_collection",
        verbose_name="Модуль",
    )
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    quantity = models.PositiveIntegerField(default=10, verbose_name="Количество на странице")
    random = models.BooleanField(default=False, verbose_name="Случайный порядок")

    class Meta:
        verbose_name = "Подборка тегов"
        verbose_name_plural = "Подборки тегов"
        ordering = ["id"]

    def __str__(self):
        return self.title


class TagCollectionItem(models.Model):
    collection = models.ForeignKey(
        TagCollection,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Подборка",
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
        verbose_name = "Тег подборки"
        verbose_name_plural = "Теги подборки"
        ordering = ["order", "id"]

    def __str__(self):
        return str(self.tag)

