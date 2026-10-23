from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dictionaries", "0006_projecttype"),
    ]

    operations = [
        migrations.AlterField(
            model_name="projecttype",
            name="name",
            field=models.CharField(max_length=100),
        ),
        migrations.AddField(
            model_name="projecttype",
            name="project_type_alias",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
