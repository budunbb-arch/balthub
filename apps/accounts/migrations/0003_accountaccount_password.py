from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_accountaccount_accountaccountgroup"),
    ]

    operations = [
        migrations.AddField(
            model_name="accountaccount",
            name="password",
            field=models.CharField(
                blank=True,
                default="",
                help_text=(
                    "Хранить только хеш, созданный штатным механизмом "
                    "хеширования Django."
                ),
                max_length=128,
                verbose_name="Хеш пароля",
            ),
        ),
    ]
