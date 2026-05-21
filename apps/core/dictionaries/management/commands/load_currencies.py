# apps/dictionaries/management/commands/load_currencies.py
from django.core.management.base import BaseCommand
from apps.dictionaries.models import Currency

class Command(BaseCommand):
    help = "Load default currencies"

    def handle(self, *args, **kwargs):
        currencies = [
            {"code": "RUR", "name": "Российский рубль", "prefix": "", "postfix": "руб."},
            {"code": "USD", "name": "Доллар США", "prefix": "$", "postfix": ""},
            {"code": "EUR", "name": "Евро", "prefix": "€", "postfix": ""},
        ]

        for cur in currencies:
            Currency.objects.update_or_create(
                code=cur["code"],
                defaults={
                    "name": cur["name"],
                    "prefix": cur.get("prefix"),
                    "postfix": cur.get("postfix")
                }
            )

        self.stdout.write("✔ Currencies loaded")
