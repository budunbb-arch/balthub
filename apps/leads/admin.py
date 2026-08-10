# apps/leads/admin.py

from django.contrib import admin
from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "added_at")
    search_fields = ("name", "phone", "email", "message")
    list_filter = ("added_at",)
