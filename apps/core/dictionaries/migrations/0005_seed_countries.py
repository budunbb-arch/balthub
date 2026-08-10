# Generated manually: наполнение справочника стран и телефонных кодов.

from django.db import migrations


COUNTRIES = [
    # (code, name, phone_code)
    ("RU", "Россия", "7"),
    ("KZ", "Казахстан", "7"),
    ("BY", "Беларусь", "375"),
    ("UA", "Украина", "380"),
    ("GE", "Грузия", "995"),
    ("AM", "Армения", "374"),
    ("AZ", "Азербайджан", "994"),
    ("UZ", "Узбекистан", "998"),
    ("KG", "Киргизия", "996"),
    ("TJ", "Таджикистан", "992"),
    ("TM", "Туркменистан", "993"),
    ("MD", "Молдова", "373"),
    ("LT", "Литва", "370"),
    ("LV", "Латвия", "371"),
    ("EE", "Эстония", "372"),
    ("PL", "Польша", "48"),
    ("DE", "Германия", "49"),
    ("FR", "Франция", "33"),
    ("IT", "Италия", "39"),
    ("ES", "Испания", "34"),
    ("TR", "Турция", "90"),
    ("AE", "ОАЭ", "971"),
    ("US", "США", "1"),
    ("CA", "Канада", "1"),
    ("GB", "Великобритания", "44"),
    ("CN", "Китай", "86"),
    ("IL", "Израиль", "972"),
    ("TH", "Таиланд", "66"),
    ("FI", "Финляндия", "358"),
    ("SE", "Швеция", "46"),
    ("NO", "Норвегия", "47"),
    ("DK", "Дания", "45"),
    ("NL", "Нидерланды", "31"),
    ("BE", "Бельгия", "32"),
    ("CH", "Швейцария", "41"),
    ("AT", "Австрия", "43"),
    ("CZ", "Чехия", "420"),
    ("SK", "Словакия", "421"),
    ("HU", "Венгрия", "36"),
    ("BG", "Болгария", "359"),
    ("RO", "Румыния", "40"),
    ("GR", "Греция", "30"),
    ("PT", "Португалия", "351"),
    ("CY", "Кипр", "357"),
    ("JP", "Япония", "81"),
    ("KR", "Южная Корея", "82"),
    ("AU", "Австралия", "61"),
]


def forwards(apps, schema_editor):
    Country = apps.get_model("dictionaries", "Country")
    for code, name, phone_code in COUNTRIES:
        Country.objects.update_or_create(
            code=code,
            defaults={"name": name, "phone_code": phone_code},
        )


def reverse(apps, schema_editor):
    Country = apps.get_model("dictionaries", "Country")
    Country.objects.filter(code__in=[c[0] for c in COUNTRIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("dictionaries", "0004_country"),
    ]

    operations = [
        migrations.RunPython(forwards, reverse),
    ]
