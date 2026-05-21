# apps/estates/developers/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Developer


@receiver([post_save, post_delete], sender=Developer)
def clear_developers_cache(sender, instance, **kwargs):
    """
    Сбрасываем кэш проектов, если изменился разработчик.
    """
    keys = cache.keys("projects_list*")
    if keys:
        cache.delete_many(keys)
