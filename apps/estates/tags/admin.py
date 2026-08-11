# apps/estates/tags/admin.py

from django.contrib import admin
from .models import Tag, ProjectTag


class ProjectTagInline(admin.TabularInline):
    model = ProjectTag
    extra = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ["name"]}
    inlines = [ProjectTagInline]
