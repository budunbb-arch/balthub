# /opt/balthub/apps/modules/admin.py

from django.contrib import admin
from .models import FooterMenuItem, TagsMenu, TagsMenuItem


@admin.register(FooterMenuItem)
class FooterMenuItemAdmin(admin.ModelAdmin):
    list_display = ("title", "url", "order", "is_active", "module")
    list_filter = ("is_active", "module")
    search_fields = ("title", "url", "module__name")
    ordering = ("order", "id")


class TagsMenuItemInline(admin.TabularInline):
    model = TagsMenuItem
    extra = 1
    fields = ("tag", "order", "is_active")


class TagsMenuInline(admin.StackedInline):
    model = TagsMenu
    extra = 0
    max_num = 1
    inlines = [TagsMenuItemInline]
    exclude = ["module"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return bool(obj and obj.pk)


@admin.register(TagsMenu)
class TagsMenuAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)
    inlines = [TagsMenuItemInline]


