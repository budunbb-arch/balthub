from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from apps.core.common.models import Module
from apps.core.models import SiteSettings
from apps.core.documents.models import Document
from apps.maps.models import MapSettings
from apps.estates.projects.models import Project
from apps.estates.houses.models import House
from apps.estates.flats.models import Flat
from apps.estates.tags.models import Tag, ProjectTag
from apps.core.dictionaries.models import City, District
from apps.core.documents.models import Document


def _clear_layout_cache():
    redis_client = cache.client.get_client()
    keys = redis_client.keys("layout:*")
    if keys:
        redis_client.delete(*keys)


def _clear_breadcrumbs_cache():
    redis_client = cache.client.get_client()
    keys = redis_client.keys("breadcrumbs:*")
    if keys:
        redis_client.delete(*keys)


def _clear_seo_cache():
    redis_client = cache.client.get_client()
    keys = redis_client.keys("seo:*")
    if keys:
        redis_client.delete(*keys)


def _clear_map_settings_cache():
    cache.delete("map_settings")


def _clear_site_settings_cache():
    cache.delete("site_settings")


def _clear_order_call_modal_cache():
    cache.delete("order_call_modal")


@receiver(post_save, sender=Module)
@receiver(post_delete, sender=Module)
def invalidate_layout_on_module_change(sender, **kwargs):
    _clear_layout_cache()


@receiver(post_save, sender=Project)
@receiver(post_delete, sender=Project)
def invalidate_project_detail_cache(sender, instance, **kwargs):
    from apps.core.cache_keys import project_detail_key
    cache.delete(project_detail_key(instance.id))


@receiver(post_save, sender=Project)
@receiver(post_delete, sender=Project)
@receiver(post_save, sender=House)
@receiver(post_delete, sender=House)
@receiver(post_save, sender=Flat)
@receiver(post_delete, sender=Flat)
@receiver(post_save, sender=Tag)
@receiver(post_delete, sender=Tag)
@receiver(post_save, sender=ProjectTag)
@receiver(post_delete, sender=ProjectTag)
@receiver(post_save, sender=City)
@receiver(post_delete, sender=City)
@receiver(post_save, sender=District)
@receiver(post_delete, sender=District)
@receiver(post_save, sender=Document)
@receiver(post_delete, sender=Document)
def invalidate_breadcrumbs_on_content_change(sender, **kwargs):
    _clear_breadcrumbs_cache()


@receiver(post_save, sender=SiteSettings)
def invalidate_seo_on_site_settings_change(sender, instance, **kwargs):
    _clear_seo_cache()
    _clear_site_settings_cache()
    _clear_order_call_modal_cache()


@receiver(post_save, sender=Document)
@receiver(post_delete, sender=Document)
def invalidate_order_call_modal_on_document_change(sender, **kwargs):
    _clear_order_call_modal_cache()


@receiver(post_save, sender=MapSettings)
def invalidate_map_settings_on_change(sender, **kwargs):
    _clear_map_settings_cache()
