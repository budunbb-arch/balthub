from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.estates.projects'
    verbose_name = 'Объекты'

    def ready(self):
        import apps.estates.projects.signals
