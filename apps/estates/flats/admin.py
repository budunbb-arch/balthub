from django.contrib import admin
from .models import Flat, FlatParams, FlatDeal


class FlatParamsInline(admin.StackedInline):
    model = FlatParams
    extra = 0
    max_num = 1
    fields = (
        "rooms",
        "rooms_alias",
        "square",
        "floor",
        "finish_type",
        "balcony_type",
        "bathroom_unit_type",
        "ceiling_height",
        "living_square",
        "kitchen_square",
    )


class FlatDealInline(admin.TabularInline):
    model = FlatDeal
    extra = 1


class FlatAdmin(admin.ModelAdmin):
    list_display = (
        "external_id",
        "house",
        "is_public",
        "is_deleted",
        "created_at",
    )
    search_fields = ("external_id", "house__project__name", "house__external_id", "slug")
    list_filter = ("is_public", "is_deleted", "house__project")
    ordering = ("house", "external_id")
    inlines = (FlatParamsInline, FlatDealInline)
