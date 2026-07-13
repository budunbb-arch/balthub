from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_add_is_disabled_to_sitesettings"),
    ]

    operations = [
        migrations.CreateModel(
            name="Parser",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Название парсера")),
                ("slug", models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Идентификатор")),
                ("is_active", models.BooleanField(default=True, verbose_name="Активен")),
                ("source_url", models.URLField(blank=True, verbose_name="URL фида")),
                ("auth_username", models.CharField(max_length=255, blank=True, verbose_name="Имя пользователя")),
                ("auth_password", models.CharField(max_length=255, blank=True, verbose_name="Пароль")),
                ("headers", models.JSONField(blank=True, null=True, verbose_name="Заголовки")),
                ("schedule", models.CharField(max_length=100, blank=True, verbose_name="Расписание", help_text="Cron-выражение, например 0 3 * * *")),
                ("last_run", models.DateTimeField(null=True, blank=True, verbose_name="Последний запуск")),
                ("last_status", models.CharField(blank=True, max_length=50, choices=[("pending", "Ожидает"), ("started", "Выполняется"), ("success", "Успешно"), ("failed", "Ошибка")], verbose_name="Статус последнего запуска")),
                ("last_message", models.TextField(blank=True, verbose_name="Сообщение последнего запуска")),
                ("last_file", models.FileField(upload_to="imports/%Y/%m/%d", blank=True, null=True, verbose_name="Последний файл")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Дата изменения")),
            ],
            options={
                "verbose_name": "Парсер",
                "verbose_name_plural": "Парсеры",
            },
        ),
        migrations.CreateModel(
            name="ParserRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("started_at", models.DateTimeField(null=True, blank=True, verbose_name="Запуск начат")),
                ("finished_at", models.DateTimeField(null=True, blank=True, verbose_name="Запуск завершён")),
                ("status", models.CharField(max_length=50, choices=[("pending", "Ожидает"), ("started", "Выполняется"), ("success", "Успешно"), ("failed", "Ошибка")], verbose_name="Статус")),
                ("message", models.TextField(blank=True, verbose_name="Сообщение")),
                ("feed_file", models.FileField(upload_to="imports/%Y/%m/%d", blank=True, null=True, verbose_name="Файл фида")),
                ("items_processed", models.IntegerField(null=True, blank=True, verbose_name="Обработано записей")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")),
                ("parser", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="runs", to="core.parser", verbose_name="Парсер")),
            ],
            options={
                "verbose_name": "Запуск парсера",
                "verbose_name_plural": "Запуски парсеров",
                "ordering": ["-started_at"],
            },
        ),
    ]
