from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccountAccount",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Имя")),
                (
                    "secret",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        verbose_name="Хеш секрета активации",
                    ),
                ),
                (
                    "secret_idle",
                    models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="Секрет действителен до",
                    ),
                ),
                ("active", models.BooleanField(default=False, verbose_name="Активен")),
                (
                    "contacts",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text=(
                            "JSON-объект: ID типа контакта из справочника типов "
                            "контактов и соответствующее значение."
                        ),
                        verbose_name="Контакты",
                    ),
                ),
            ],
            options={
                "verbose_name": "Пользователь сайта",
                "verbose_name_plural": "Пользователи сайта",
                "db_table": "account_account",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="AccountAccountGroup",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "account_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="account_group_links",
                        to="accounts.accountaccount",
                        verbose_name="Пользователь сайта",
                    ),
                ),
                (
                    "account_group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="account_links",
                        to="accounts.accountgroup",
                        verbose_name="Группа пользователей",
                    ),
                ),
            ],
            options={
                "verbose_name": "Связь пользователя с группой",
                "verbose_name_plural": "Связи пользователей с группами",
                "db_table": "account_account_groups",
            },
        ),
        migrations.AddField(
            model_name="accountaccount",
            name="groups",
            field=models.ManyToManyField(
                related_name="accounts",
                through="accounts.AccountAccountGroup",
                to="accounts.accountgroup",
                verbose_name="Группы",
            ),
        ),
        migrations.AddConstraint(
            model_name="accountaccountgroup",
            constraint=models.UniqueConstraint(
                fields=("account_account", "account_group"),
                name="unique_account_account_group",
            ),
        ),
    ]
