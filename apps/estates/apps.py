from django.apps import AppConfig


class EstatesConfig(AppConfig):
    name = "apps.estates"
    verbose_name = "Объекты"

    def ready(self):
        import apps.estates.signals
