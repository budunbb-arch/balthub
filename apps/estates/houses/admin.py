from django.contrib import admin
from apps.core.common.admin import SoftDeleteAdmin
from .models import House, HouseParams


class HouseParamsInline(admin.StackedInline):
    model = HouseParams
    extra = 0
    max_num = 1
    fields = (
        "address",
        "corpus",
        "phase",
        "deadline",
        "deadline_year",
        "floors",
        "house_structure_type",
        "building_status",
        "lift",
        "parking",
        "latitude",
        "longitude",
    )


class HouseAdmin(SoftDeleteAdmin):
    list_display = (
        "external_id",
        "project",
        "is_public",
        "is_deleted",
        "created_at",
    )
    search_fields = ("external_id", "project__name", "slug")
    list_filter = ("is_public", "is_deleted", "project")
    ordering = ("project", "external_id")
    inlines = (HouseParamsInline,)
