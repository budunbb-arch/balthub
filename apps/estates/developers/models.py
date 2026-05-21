# /opt/balthub/apps/estates/developers/models.py
from django.db import models
from apps.core.common.models import BaseModel
from apps.core.common.mixins import SeoMixin
from django.utils.text import slugify


class Developer(BaseModel, SeoMixin):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, max_length=255, blank=True, null=True)
    logo = models.ImageField(upload_to="developers/logos/", null=True, blank=True)

    class Meta:
        db_table = "developers"
        verbose_name = "Застройщик"
        verbose_name_plural = "Застройщики"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)

            slug = base_slug
            i = 1

            while Developer.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{i}"
                i += 1

            self.slug = slug

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
