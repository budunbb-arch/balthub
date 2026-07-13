from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core.common'
    verbose_name = 'Настройки'

    def ready(self):
        import apps.core.common.signals
