from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0010_alter_module_type_account"),
    ]

    operations = [
        migrations.AlterField(
            model_name="module",
            name="type",
            field=models.CharField(
                choices=[
                    ("latest_projects", "Последние проекты"),
                    ("html", "HTML модуль"),
                    ("feedback", "Обратная связь"),
                    ("main_menu", "Главное меню"),
                    ("footer_menu", "Меню футера"),
                    ("tags_menu", "Меню тегов"),
                    ("tag_collection", "Подборка тегов"),
                    ("project_description", "Описание проекта"),
                    ("house_description", "Описание дома"),
                    ("flat_description", "Описание квартиры"),
                    ("account", "Аккаунт пользователя"),
                ],
                default="latest_projects",
                max_length=50,
                verbose_name="Тип модуля",
            ),
        ),
    ]
