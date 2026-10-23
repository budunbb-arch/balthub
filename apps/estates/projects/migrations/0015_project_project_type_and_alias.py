import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dictionaries", "0006_projecttype"),
        ("projects", "0014_project_tags"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="project_type",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="projects",
                to="dictionaries.projecttype",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="project_type_alias",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
