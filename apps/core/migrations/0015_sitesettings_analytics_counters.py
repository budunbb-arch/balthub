from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_sitesettings_addresses'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='analytics_counters',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="JSON-список: [{'name': 'Яндекс Метрика', 'code': '<script>...</script>'}]",
                verbose_name='Счётчики аналитики',
            ),
        ),
    ]