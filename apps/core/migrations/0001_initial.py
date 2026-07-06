from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_name', models.CharField(default='Balthub', max_length=255, verbose_name='Название сайта')),
                ('default_title', models.CharField(blank=True, max_length=255, verbose_name='Заголовок по умолчанию')),
                ('default_description', models.TextField(blank=True, verbose_name='Описание по умолчанию')),
                ('default_keywords', models.TextField(blank=True, verbose_name='Ключевые слова по умолчанию')),
                ('default_canonical', models.URLField(blank=True, verbose_name='Канонический URL по умолчанию')),
                ('default_robots', models.CharField(default='index, follow', max_length=50, verbose_name='Robots по умолчанию')),
            ],
            options={
                'db_table': 'common_sitesettings',
                'verbose_name': 'Настройки сайта',
                'verbose_name_plural': 'Настройки сайта',
            },
        ),
    ]
