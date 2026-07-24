from django.contrib import admin
from .models import MapSettings


@admin.register(MapSettings)
class MapSettingsAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return not MapSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False