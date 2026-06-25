# apps/estates/projects/models.py

from django.db import models
from transliterate import translit
from slugify import slugify

from apps.core.common.mixins import UrlMixin, SeoMixin
from apps.core.common.models import BaseModel
from apps.estates.developers.models import Developer
from apps.core.dictionaries.models import City, District, PropertyCategory, PropertyType
from .queries import ProjectQuerySet


def ru_slug(text):
    return slugify(translit(text, 'ru', reversed=True))


class Project(BaseModel, UrlMixin, SeoMixin):

    objects = ProjectQuerySet.as_manager()

    external_id = models.CharField(max_length=100, unique=True, null=True)

    name = models.CharField(max_length=255)

    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = ru_slug(self.name)

        RESERVED_SLUGS = ["projects", "houses", "flats"]

        if self.slug in RESERVED_SLUGS:
            self.slug = f"{self.slug}-{self.id}"

        super().save(*args, **kwargs)

    developer = models.ForeignKey(
        Developer,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="projects"
    )

    
    def get_absolute_url(self):
        return self.get_url("project_detail", self.slug)

    def get_houses_url(self):
        return self.get_url("houses_project", self.slug)

    def __str__(self):
        return self.name


class ProjectParams(models.Model):
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name="params"
    )

    city = models.ForeignKey(
        City,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )

    district = models.ForeignKey(
        District,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )

    property_type = models.ForeignKey(
        PropertyType,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )


    property_category = models.ForeignKey(
        PropertyCategory,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )



class ProjectDescription(models.Model):
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name="description"
    )

    description = models.TextField()

    hash = models.CharField(max_length=64, unique=True, null=True, db_index=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Description for {self.project}"


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="images"
    )

    image = models.URLField()

    class Meta:
        unique_together = ("project", "image")
