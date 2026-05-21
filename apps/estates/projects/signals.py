from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from apps.estates.projects.models import Project
from apps.core.cache_keys import project_list_key, project_detail_key


@receiver([post_save, post_delete], sender=Project)
def project_changed(sender, instance, **kwargs):
    cache.delete(project_list_key())
    cache.delete(project_detail_key(instance.id))
