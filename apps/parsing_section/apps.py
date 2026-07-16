# apps/parsing_section/apps.py

from django.apps import AppConfig


class ParsingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.parsing_section"
    verbose_name = "Парсинг"