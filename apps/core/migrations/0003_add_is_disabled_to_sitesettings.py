from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_alter_sitesettings_table"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="is_disabled",
            field=models.BooleanField(
                default=False,
                verbose_name="Выключить сайт",
                help_text="Показывать заглушку всем пользователям, кроме администраторов.",
            ),
        ),
    ]
