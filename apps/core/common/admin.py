# apps/core/common/admin.py

from django.contrib import admin
from .models import Module

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("name", "position", "route", "is_active", "order")
    list_filter = ("position", "is_active")
    search_fields = ("name", "template", "route")
    ordering = ("position", "order")
