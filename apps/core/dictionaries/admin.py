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
        City,
    ],
    DictionaryAdmin,
)

admin.site.register(Currency, CurrencyAdmin)
admin.site.register(ContactType, ContactTypeAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(District, DistrictAdmin)
