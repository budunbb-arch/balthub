from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from apps.estates.houses.models import House
from apps.core.cache_keys import house_list_key, houses_project_key, house_flats_key


@receiver([post_save, post_delete], sender=House)
def house_changed(sender, instance, **kwargs):
    cache.delete(house_list_key())
    cache.delete(houses_project_key(instance.project_id))
    cache.delete(house_flats_key(instance.id))
