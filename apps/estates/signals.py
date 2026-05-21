from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from apps.estates.projects.models import Project
from apps.estates.houses.models import House
from apps.estates.flats.models import Flat


# =========================
# PROJECTS
# =========================

@receiver([post_save, post_delete], sender=Project)
def invalidate_project_cache(sender, instance, **kwargs):
    cache.delete("project_list")
    cache.delete(f"project_detail_{instance.id}")


# =========================
# HOUSES
# =========================

@receiver([post_save, post_delete], sender=House)
def invalidate_house_cache(sender, instance, **kwargs):
    cache.delete("house_list")
    cache.delete(f"houses_project_{instance.project_id}")
    cache.delete(f"house_flats_{instance.id}")


# =========================
# FLATS
# =========================

@receiver([post_save, post_delete], sender=Flat)
def invalidate_flat_cache(sender, instance, **kwargs):
    cache.delete(f"house_flats_{instance.house_id}")
