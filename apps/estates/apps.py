from django.apps import AppConfig


class EstatesConfig(AppConfig):
    name = "apps.estates"

    def ready(self):
        import apps.estates.signals
