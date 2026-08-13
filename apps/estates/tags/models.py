# apps/estates/tags/models.py

from django.db import models
from apps.core.common.mixins import SeoMixin


class Tag(SeoMixin):
    name = models.CharField(max_length=100, unique=True, verbose_name="Тег")
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from slugify import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ProjectTag(models.Model):
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="project_tags")
    tag = models.ForeignKey("tags.Tag", on_delete=models.CASCADE, related_name="project_tags")

    class Meta:
        unique_together = ("project", "tag")
        verbose_name = "Тег проекта"
        verbose_name_plural = "Теги проектов"

    def __str__(self):
        return f"{self.project.name} — {self.tag.name}"
