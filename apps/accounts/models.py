from django.db import models


class AccountGroup(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="Название",
    )
    employee = models.BooleanField(
        default=False,
        verbose_name="Сотрудник",
    )
    client = models.BooleanField(
        default=False,
        verbose_name="Клиент",
    )
    developer_contact = models.BooleanField(
        default=False,
        verbose_name="Контакт застройщика",
    )
    blog_author = models.BooleanField(
        default=False,
        verbose_name="Автор блога",
    )
    blog_editor = models.BooleanField(
        default=False,
        verbose_name="Редактор блога",
    )
    upload_files = models.BooleanField(
        default=False,
        verbose_name="Загрузка файлов",
    )

    class Meta:
        db_table = "account_groups"
        verbose_name = "Группа пользователей"
        verbose_name_plural = "Группы пользователей"
        ordering = ("name",)

    def __str__(self):
        return self.name


class AccountAccount(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="Имя",
    )
    password = models.CharField(
        max_length=128,
        blank=True,
        default="",
        verbose_name="Хеш пароля",
        help_text="Хранить только хеш, созданный штатным механизмом хеширования Django.",
    )
    secret = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Хеш секрета активации",
    )
    secret_idle = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Секрет действителен до",
    )
    active = models.BooleanField(
        default=False,
        verbose_name="Активен",
    )
    contacts = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Контакты",
        help_text=(
            "JSON-объект: ID типа контакта из справочника типов контактов "
            "и соответствующее значение."
        ),
    )
    groups = models.ManyToManyField(
        AccountGroup,
        through="AccountAccountGroup",
        related_name="accounts",
        verbose_name="Группы",
    )

    class Meta:
        db_table = "account_account"
        verbose_name = "Пользователь сайта"
        verbose_name_plural = "Пользователи сайта"
        ordering = ("name",)

    def __str__(self):
        return self.name


class AccountAccountGroup(models.Model):
    account_account = models.ForeignKey(
        AccountAccount,
        on_delete=models.CASCADE,
        related_name="account_group_links",
        verbose_name="Пользователь сайта",
    )
    account_group = models.ForeignKey(
        AccountGroup,
        on_delete=models.CASCADE,
        related_name="account_links",
        verbose_name="Группа пользователей",
    )

    class Meta:
        db_table = "account_account_groups"
        verbose_name = "Связь пользователя с группой"
        verbose_name_plural = "Связи пользователей с группами"
        constraints = [
            models.UniqueConstraint(
                fields=("account_account", "account_group"),
                name="unique_account_account_group",
            ),
        ]

    def __str__(self):
        return f"{self.account_account} — {self.account_group}"
