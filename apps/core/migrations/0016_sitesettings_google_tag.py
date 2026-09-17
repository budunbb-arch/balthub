from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0015_sitesettings_analytics_counters"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="google_tag",
            field=models.CharField(
                blank=True,
                help_text="Значение для meta name=google-site-verification.",
                max_length=255,
                verbose_name="Google tag",
            ),
        ),
    ]
