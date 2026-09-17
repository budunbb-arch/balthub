from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0016_sitesettings_google_tag"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="yandex_tag",
            field=models.CharField(
                blank=True,
                help_text="Значение для meta name=yandex-verification.",
                max_length=255,
                verbose_name="Yandex tag",
            ),
        ),
    ]
