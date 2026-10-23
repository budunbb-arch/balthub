from django.contrib import admin
from .models import (
    BalconyType,
    BathroomUnitType,
    BuildingStatus,
    City,
    ContactType,
    Country,
    Currency,
    DealType,
    District,
    FinishType,
    HouseStructureType,
    PropertyCategory,
    ProjectType,
    PropertyType,
)


class DictionaryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


class CurrencyAdmin(DictionaryAdmin):
    list_display = ("code", "name", "prefix", "postfix")
    search_fields = ("code", "name")


class ContactTypeAdmin(DictionaryAdmin):
    list_display = ("code", "name", "prefix", "postfix")
    search_fields = ("code", "name")


class CountryAdmin(DictionaryAdmin):
    list_display = ("code", "name", "phone_code")
    search_fields = ("code", "name", "phone_code")


class ProjectTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "project_type_alias", "default")
    list_filter = ("default",)
    search_fields = ("name", "project_type_alias")
    ordering = ("name",)


class CityAdmin(DictionaryAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")


class DistrictAdmin(admin.ModelAdmin):
    list_display = ("city", "name")
    list_filter = ("city",)
    search_fields = ("name", "city__name")
    ordering = ("city__name", "name")


admin.site.register(
    [
        DealType,
        PropertyType,
        PropertyCategory,
        FinishType,
        BalconyType,
        BathroomUnitType,
        HouseStructureType,
        BuildingStatus,
    ],
    DictionaryAdmin,
)

admin.site.register(City, CityAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(ContactType, ContactTypeAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(ProjectType, ProjectTypeAdmin)
admin.site.register(District, DistrictAdmin)
