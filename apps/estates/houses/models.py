# apps/estates/houses/models.py

from django.db import models
from .queries import HouseQuerySet
from transliterate import translit
from slugify import slugify

from apps.core.common.mixins import UrlMixin, SeoMixin
from apps.core.common.models import BaseModel
from apps.estates.projects.models import Project
from apps.core.dictionaries.models import (
    HouseStructureType,
    BuildingStatus,
)


class House(BaseModel, UrlMixin, SeoMixin):
    objects = HouseQuerySet.as_manager()
    
    external_id = models.CharField(max_length=100, unique=True, null=True)

    slug = models.SlugField(max_length=255, null=True, blank=True)


    def ensure_slug(self):

        if self.slug:
            return

        base_slug = slugify(self.external_id or f"{Project.name}-dom")

        slug = base_slug
        i = 1

        while House.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}{i}"
            i += 1

        self.slug = slug


    def save(self, *args, **kwargs):
        self.ensure_slug()
        super().save(*args, **kwargs)

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="houses"
    )

    image = models.URLField(null=True, blank=True)
    plan = models.URLField(null=True, blank=True)

    class Meta:
        unique_together = ("project", "slug")

    def get_absolute_url(self):
        return self.get_url("house_detail", self.project.slug, self.slug)

    def __str__(self):
        return f"House {self.external_id}"


class HouseParams(models.Model):
    house = models.OneToOneField(
        House,
        on_delete=models.CASCADE,
        related_name="params"
    )

    address = models.CharField(max_length=255, null=True, blank=True)
    corpus = models.CharField(max_length=255, null=True, blank=True)
    phase = models.CharField(max_length=255, null=True, blank=True)

    deadline = models.CharField(max_length=50, null=True, blank=True)
    deadline_year = models.IntegerField(null=True, blank=True)

    floors = models.IntegerField(null=True, blank=True)

    house_structure_type = models.ForeignKey(
        HouseStructureType,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )

    building_status = models.ForeignKey(
        BuildingStatus,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )

    lift = models.BooleanField(default=True, null=True)
    parking = models.BooleanField(default=True, null=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
