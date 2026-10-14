from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("modules", "0017_tagcollection_tagcollectionitem"),
    ]

    operations = [
        migrations.AddField(
            model_name="tagcollectionitem",
            name="image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="tag_collections/",
                verbose_name="Изображение",
            ),
        ),
        migrations.AddField(
            model_name="tagcollectionitem",
            name="description",
            field=models.CharField(
                blank=True,
                default="",
                max_length=255,
                verbose_name="Краткое описание",
            ),
        ),
    ]