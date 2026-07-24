# /opt/balthub/apps/core/common/mixins.py

from django.urls import reverse
from django.db import models


class UrlMixin:
    """
    Универсальный миксин для генерации URL.
    """

    def get_url(self, name, *args, **kwargs):
        if not args and not kwargs:
            if not getattr(self, "slug", None):
                raise ValueError("Slug is not set for URL generation")
            args = [self.slug]

        return reverse(name, args=args, kwargs=kwargs)

    def get_absolute_url(self):
        """
        Должен быть переопределён в модели
        """
        raise NotImplementedError("Define get_absolute_url() or set default behavior")


class SeoMixin(models.Model):

    meta_title = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    meta_keywords = models.TextField(blank=True, null=True)

    seo_h1 = models.CharField(max_length=255, blank=True, null=True)

    canonical_url = models.URLField(blank=True, null=True)

    robots_index = models.BooleanField(default=True)
    robots_follow = models.BooleanField(default=True)

    class Meta:
        abstract = True