import apps.core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0017_sitesettings_yandex_tag"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="template",
            field=models.CharField(
                choices=apps.core.models.get_site_template_choices,
                default="default",
                max_length=100,
                verbose_name="Шаблон сайта",
            ),
        ),
    ]