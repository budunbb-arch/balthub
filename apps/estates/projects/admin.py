from django.contrib import admin
from .models import Project, ProjectParams, ProjectDescription, ProjectImage


class ProjectParamsInline(admin.StackedInline):
    model = ProjectParams
    extra = 0
    max_num = 1
    fields = (
        "city",
        "district",
        "property_type",
        "property_category",
    )


class ProjectDescriptionInline(admin.StackedInline):
    model = ProjectDescription
    extra = 0
    max_num = 1
    fields = ("description",)


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1

class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "developer",
        "is_public",
        "is_deleted",
        "created_at",
    )
    search_fields = ("name", "external_id", "developer__name")
    list_filter = ("is_public", "is_deleted", "developer")
    ordering = ("name",)
    inlines = (ProjectParamsInline, ProjectDescriptionInline, ProjectImageInline)
