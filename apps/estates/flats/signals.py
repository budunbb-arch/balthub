from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from apps.estates.flats.models import Flat, FlatDeal, FlatParams
from apps.core.cache_keys import house_flats_key

def clear_house_flats_cache(house_id):
    cache.delete(house_flats_key(house_id))

"""
def clear_house_flats_cache(house_id):
    cache.delete(f"house_flats_{house_id}")
"""


# --- Flat ---
@receiver(post_save, sender=Flat)
@receiver(post_delete, sender=Flat)
def flat_changed(sender, instance, **kwargs):
    clear_house_flats_cache(instance.house_id)


# --- FlatParams ---
@receiver(post_save, sender=FlatParams)
@receiver(post_delete, sender=FlatParams)
def flat_params_changed(sender, instance, **kwargs):
    clear_house_flats_cache(instance.flat.house_id)


# --- FlatDeal ---
@receiver(post_save, sender=FlatDeal)
@receiver(post_delete, sender=FlatDeal)
def flat_deal_changed(sender, instance, **kwargs):
    clear_house_flats_cache(instance.flat.house_id)
