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
    try:
        # Используем встроенную функцию из context processor
        from apps.core.engines.context_processors import clear_layout_cache
        clear_layout_cache()
    except Exception as e:
        # Fallback: удаляем через стандартный cache API
        try:
            keys = cache.keys("layout:*")
            if keys:
                cache.delete_many(keys)
        except Exception:
            # В крайнем случае ничего не делаем, но логируем
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to clear module cache: {e}")
