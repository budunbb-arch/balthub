from django.db import migrations, models
from slugify import slugify


def populate_city_slugs(apps, schema_editor):
    City = apps.get_model("dictionaries", "City")
    database = schema_editor.connection.alias
    used_slugs = set()

    for city in City.objects.using(database).order_by("pk"):
        base_slug = slugify(city.name) or f"city-{city.pk}"
        slug = base_slug
        suffix = 1
        while slug in used_slugs:
            suffix += 1
            slug = f"{base_slug}-{suffix}"

        city.slug = slug
        city.save(using=database, update_fields=["slug"])
        used_slugs.add(slug)


def clear_city_slugs(apps, schema_editor):
    City = apps.get_model("dictionaries", "City")
    City.objects.using(schema_editor.connection.alias).update(slug=None)


class Migration(migrations.Migration):

    dependencies = [
        ("dictionaries", "0007_projecttype_alias_and_name_length"),
    ]

    operations = [
        migrations.AddField(
            model_name="city",
            name="slug",
            field=models.SlugField(blank=True, max_length=255, null=True, unique=True),
        ),
        migrations.RunPython(populate_city_slugs, clear_city_slugs),
        migrations.AlterField(
            model_name="city",
            name="slug",
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
    ]
