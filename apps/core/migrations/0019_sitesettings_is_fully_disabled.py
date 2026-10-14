from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0018_sitesettings_template"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="is_fully_disabled",
            field=models.BooleanField(
                default=False,
                help_text="Показывать отдельную заглушку на всех публичных страницах, включая формы и API.",
                verbose_name="Полностью выключить сайт",
            ),
        ),
    ]
