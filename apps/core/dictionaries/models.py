# apps/dictionaries/models.py

from django.db import models


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


class City(BaseDictionary):
    pass


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


class Meta:
    abstract = True
    indexes = [
        models.Index(fields=["name"]),
    ]
