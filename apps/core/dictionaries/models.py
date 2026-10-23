# apps/dictionaries/models.py

from django.db import models
from slugify import slugify

from apps.core.common.mixins import SlugifyMixin


class BaseDictionary(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Currency(BaseDictionary):
    code = models.CharField(max_length=10, unique=True)
    prefix = models.CharField(max_length=10, blank=True, null=True)
    postfix = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.code} — {self.name}"


class DealType(BaseDictionary):
    pass


class PropertyType(BaseDictionary):
    pass


class ProjectType(models.Model):
    name = models.CharField(max_length=100)
    project_type_alias = models.CharField(max_length=255, blank=True)
    default = models.BooleanField(null=True, blank=True, default=None)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("default",),
                condition=models.Q(default=True),
                name="unique_default_project_type",
            ),
        ]

    def __str__(self):
        return self.name


class PropertyCategory(BaseDictionary):
    pass


class FinishType(BaseDictionary):
    pass


class BalconyType(BaseDictionary):
    pass


class BathroomUnitType(BaseDictionary):
    pass


class HouseStructureType(BaseDictionary):
    pass


class BuildingStatus(BaseDictionary):
    pass


class City(BaseDictionary, SlugifyMixin):
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def build_slug_base(self):
        return slugify(self.name) or f"city-{self.pk or 'new'}"

    def save(self, *args, **kwargs):
        self.ensure_slug()
        super().save(*args, **kwargs)


class District(models.Model):
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="districts"
    )

    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ("city", "name")

    def __str__(self):
        return f"{self.city} - {self.name}"
    

class ContactType(BaseDictionary):
    code = models.CharField(max_length=50, unique=True)
    prefix = models.CharField(max_length=50, blank=True, null=True)
    postfix = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name = "Тип контакта"
        verbose_name_plural = "Типы контактов"


class Country(BaseDictionary):
    code = models.CharField(max_length=10, unique=True, verbose_name="Код страны (ISO)")
    phone_code = models.CharField(
        max_length=10,
        verbose_name="Телефонный код",
        help_text="Цифры без плюса. Например: 7, 375, 380",
    )

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} — {self.name} (+{self.phone_code})"


class Meta:
    abstract = True
    indexes = [
        models.Index(fields=["name"]),
    ]
