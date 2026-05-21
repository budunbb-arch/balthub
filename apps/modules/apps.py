from django.apps import AppConfig


class ModulesConfig(AppConfig):
    name = "apps.modules"

    def ready(self):
        from .registry import autodiscover_modules
        autodiscover_modules()
