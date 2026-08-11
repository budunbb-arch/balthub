# apps/estates/admin.py

from django.contrib import admin
from apps.estates.models import DeveloperProxy, ProjectProxy, HouseProxy, FlatProxy, TagProxy

from apps.estates.developers.admin import DeveloperAdmin
from apps.estates.projects.admin import ProjectAdmin
from apps.estates.houses.admin import HouseAdmin
from apps.estates.flats.admin import FlatAdmin
from apps.estates.tags.admin import TagAdmin


admin.site.register(DeveloperProxy, DeveloperAdmin)
admin.site.register(ProjectProxy, ProjectAdmin)
admin.site.register(HouseProxy, HouseAdmin)
admin.site.register(FlatProxy, FlatAdmin)
admin.site.register(TagProxy, TagAdmin)
