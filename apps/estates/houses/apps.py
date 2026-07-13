from django.apps import AppConfig


class HousesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.estates.houses'
    verbose_name = 'Объекты'

    def ready(self):
        import apps.estates.houses.signals
