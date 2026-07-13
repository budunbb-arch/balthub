from django.apps import AppConfig


class DevelopersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.estates.developers'
    verbose_name = 'Объекты'

    def ready(self):
        import apps.estates.developers.signals
