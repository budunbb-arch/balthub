from django.db import migrations, models
import django.db.models.deletion


def create_default_items(apps, schema_editor):
    Module = apps.get_model("core", "Module")
    MainMenuItem = apps.get_model("modules", "MainMenuItem")
    database = schema_editor.connection.alias
    default_items = [
        ("Все ЖК", "section", "/estates/projects/"),
        ("Калининград", "link", "/estates/geography/kaliningrad/"),
        ("Пригород", "link", "/estates/tags/prigorod/"),
        ("Побережье", "link", "/estates/tags/poberezhe/"),
        ("Контакты", "section", "/feedback/"),
    ]

    modules = Module.objects.using(database).filter(
        position="main_menu",
        template__endswith="main_menu.html",
    )
    for module in modules:
        MainMenuItem.objects.using(database).bulk_create([
            MainMenuItem(
                module_id=module.pk,
                name=name,
                type=item_type,
                url=url,
                is_active=True,
                range=order,
            )
            for order, (name, item_type, url) in enumerate(default_items)
        ])


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0011_add_main_menu_module_type"),
        ("core", "0019_sitesettings_is_fully_disabled"),
        ("modules", "0018_tagcollectionitem_image_description"),
    ]

    operations = [
        migrations.CreateModel(
            name="MainMenuItem",
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
                    "type",
                    models.CharField(
                        choices=[("section", "Раздел"), ("link", "Ссылка")],
                        default="section",
                        max_length=10,
                        verbose_name="Тип",
                    ),
                ),
                ("url", models.CharField(max_length=2048, verbose_name="URL")),
                (
                    "css_class",
                    models.CharField(
                        blank=True,
                        db_column="class",
                        default="",
                        max_length=255,
                        verbose_name="Дополнительный класс",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="Активен")),
                ("range", models.PositiveIntegerField(default=0, verbose_name="Порядок")),
                (
                    "module",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="main_menu_items",
                        to="core.module",
                        verbose_name="Модуль",
                    ),
                ),
            ],
            options={
                "verbose_name": "Пункт главного меню",
                "verbose_name_plural": "Пункты главного меню",
                "db_table": "modules_mainmenu",
                "ordering": ["range", "id"],
            },
        ),
        migrations.RunPython(create_default_items, migrations.RunPython.noop),
    ]
