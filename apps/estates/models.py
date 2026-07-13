from apps.estates.developers.models import Developer
from apps.estates.projects.models import Project
from apps.estates.houses.models import House
from apps.estates.flats.models import Flat


class DeveloperProxy(Developer):
    class Meta:
        proxy = True
        app_label = "estates"
        verbose_name = Developer._meta.verbose_name
        verbose_name_plural = Developer._meta.verbose_name_plural


class ProjectProxy(Project):
    class Meta:
        proxy = True
        app_label = "estates"
        verbose_name = Project._meta.verbose_name
        verbose_name_plural = Project._meta.verbose_name_plural


class HouseProxy(House):
    class Meta:
        proxy = True
        app_label = "estates"
        verbose_name = House._meta.verbose_name
        verbose_name_plural = House._meta.verbose_name_plural


class FlatProxy(Flat):
    class Meta:
        proxy = True
        app_label = "estates"
        verbose_name = Flat._meta.verbose_name
        verbose_name_plural = Flat._meta.verbose_name_plural
