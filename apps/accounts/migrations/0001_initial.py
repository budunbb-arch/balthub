from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AccountGroup",
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
                ("name", models.CharField(max_length=255, verbose_name="Название")),
                (
                    "employee",
                    models.BooleanField(default=False, verbose_name="Сотрудник"),
                ),
                (
                    "client",
                    models.BooleanField(default=False, verbose_name="Клиент"),
                ),
                (
                    "developer_contact",
                    models.BooleanField(
                        default=False,
                        verbose_name="Контакт застройщика",
                    ),
                ),
                (
                    "blog_author",
                    models.BooleanField(default=False, verbose_name="Автор блога"),
                ),
                (
                    "blog_editor",
                    models.BooleanField(default=False, verbose_name="Редактор блога"),
                ),
                (
                    "upload_files",
                    models.BooleanField(default=False, verbose_name="Загрузка файлов"),
                ),
            ],
            options={
                "verbose_name": "Группа пользователей",
                "verbose_name_plural": "Группы пользователей",
                "db_table": "account_groups",
                "ordering": ("name",),
            },
        ),
    ]
