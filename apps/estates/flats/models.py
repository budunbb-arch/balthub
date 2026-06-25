# /opt/balthub/apps/estates/flats/models.py

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from apps.core.common.models import BaseModel
from apps.core.common.mixins import UrlMixin, SeoMixin
from apps.estates.houses.models import House
from apps.core.dictionaries.models import (
    PropertyType,
    FinishType,
    BalconyType,
    BathroomUnitType,
    DealType,
    Currency,
)
from .queries import FlatQuerySet


class Flat(BaseModel, UrlMixin, SeoMixin):

    objects = FlatQuerySet.as_manager()
    external_id = models.CharField(max_length=100, unique=True, null=True)

    slug = models.SlugField(max_length=50, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            number = self.number or ""

            base_slug = slugify(f"kv{number}") if number else None

            if not base_slug:
                super().save(*args, **kwargs)
                base_slug = f"kv{self.id}"

            slug = base_slug
            counter = 1

            while Flat.objects.filter(
                house=self.house,
                slug=slug
            ).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name="flats"
    )

    number = models.CharField(max_length=32, null=True, blank=True)
    plan = models.URLField(null=True, blank=True)

    class Meta:
        unique_together = ("house", "slug")

    def get_absolute_url(self):
        return reverse(
            "flat_detail",
            args=[
                self.house.project.slug,
                self.house.slug,
                self.slug
            ]
        )

    def __str__(self):
        return f"Flat {self.external_id}"


class FlatParams(models.Model):
    flat = models.OneToOneField(
        Flat,
        on_delete=models.CASCADE,
        related_name="params"
    )

    rooms = models.IntegerField(null=True, blank=True)
    rooms_alias = models.CharField(max_length=50, null=True, blank=True)

    square = models.FloatField(null=True, blank=True)
    floor = models.IntegerField(null=True, blank=True)

    finish_type = models.ForeignKey(
        FinishType,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )

    balcony_type = models.ForeignKey(
        BalconyType,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )

    bathroom_unit_type = models.ForeignKey(
        BathroomUnitType,
        null=True, blank=True,
        on_delete=models.SET_NULL
    )

    ceiling_height = models.FloatField(null=True, blank=True)

    living_square = models.FloatField(null=True, blank=True)
    kitchen_square = models.FloatField(null=True, blank=True)


class FlatDeal(models.Model):
    flat = models.ForeignKey(
        Flat,
        on_delete=models.CASCADE,
        related_name="deals"
    )
    deal_type = models.ForeignKey(
        DealType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)

    mortgage = models.BooleanField(default=True)
    haggle = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("flat", "deal_type")

    def __str__(self):
        return f"{self.flat} - {self.deal_type}"
