# apps/core/common/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings
from .models import Module


@receiver([post_save, post_delete], sender=Module)
def clear_module_cache(sender, instance, **kwargs):
    """
    Сбрасываем кэш layout при изменении модулей.
    """
    # Для простоты — сбросим все layout-кэши
    keys = cache.keys("layout:*")
    if keys:
        cache.delete_many(keys)
