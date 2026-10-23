from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dictionaries", "0005_seed_countries"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectType",
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
                ("name", models.TextField()),
                ("default", models.BooleanField(blank=True, default=None, null=True)),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        condition=models.Q(("default", True)),
                        fields=("default",),
                        name="unique_default_project_type",
                    ),
                ],
            },
        ),
    ]
