from django.apps import AppConfig


class FlatsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.estates.flats'

    def ready(self):
        import apps.estates.flats.signals
