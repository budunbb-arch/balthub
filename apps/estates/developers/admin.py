from django.contrib import admin
from .models import Developer


@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_public", "created_at")
    search_fields = ("name",)
    list_filter = ("is_public", "is_deleted")
