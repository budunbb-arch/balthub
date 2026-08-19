# /opt/balthub/apps/estates/developers/models.py

from django.db import models
from slugify import slugify

from apps.core.common.models import BaseModel
from apps.core.common.mixins import SeoMixin, SlugifyMixin
from .queries import DeveloperQuerySet


class Developer(BaseModel, SeoMixin, SlugifyMixin):

    objects = DeveloperQuerySet.as_manager()

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, max_length=255, blank=True, null=True)
    logo = models.ImageField(upload_to="developers/logos/", null=True, blank=True)

    class Meta:
        db_table = "developers"
        verbose_name = "Застройщик"
        verbose_name_plural = "Застройщики"
        ordering = ["name"]

    def build_slug_base(self):
        return slugify(self.name)

    def save(self, *args, **kwargs):
        self.ensure_slug()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class DeveloperConnect(models.Model):
    developer = models.ForeignKey(
        "developers.Developer",
        on_delete=models.CASCADE,
        related_name="%(class)ss"
    )

    class Meta:
        abstract = True


class DeveloperDescription(DeveloperConnect):
    text_description = models.TextField()


class DeveloperContact(DeveloperConnect):
    contact_type = models.ForeignKey(
        "dictionaries.ContactType",
        on_delete=models.CASCADE
    )
    value = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)



class DeveloperDepartment(DeveloperConnect):
    name = models.CharField(max_length=255)


class DepartmentContact(models.Model):
    department = models.ForeignKey(
        "developers.DeveloperDepartment",
        on_delete=models.CASCADE,
        related_name="contacts"
    )

    contact_type = models.ForeignKey(
        "dictionaries.ContactType",
        on_delete=models.CASCADE
    )

    value = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
