# apps/estates/tags/models.py

from django.db import models
from apps.core.common.mixins import SeoMixin
from apps.core.common.models import BaseModel


class Tag(SeoMixin, BaseModel):
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


class FlatTag(models.Model):
    flat = models.ForeignKey("flats.Flat", on_delete=models.CASCADE, related_name="flat_tags")
    tag = models.ForeignKey("tags.Tag", on_delete=models.CASCADE, related_name="flat_tags")

    class Meta:
        unique_together = ("flat", "tag")
        verbose_name = "Тег квартиры"
        verbose_name_plural = "Теги квартир"

    def __str__(self):
        return f"{self.flat} — {self.tag.name}"


class AutoTagTask(models.Model):
    OBJECT_TYPE_FLAT = "flat"
    OBJECT_TYPE_PROJECT = "project"
    OBJECT_TYPE_CHOICES = [
        (OBJECT_TYPE_FLAT, "Квартира"),
        (OBJECT_TYPE_PROJECT, "Проект"),
    ]

    tag = models.ForeignKey("tags.Tag", on_delete=models.CASCADE, related_name="auto_tasks")
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPE_CHOICES, verbose_name="Тип объекта")
    autostart = models.BooleanField(default=False, verbose_name="Автостарт")
    triggers = models.JSONField(default=list, blank=True, verbose_name="Признаки")

    class Meta:
        verbose_name = "Автотег задание"
        verbose_name_plural = "Автотег задания"
        ordering = ["id"]

    def __str__(self):
        return f"{self.tag.name} — {self.get_object_type_display()}"
