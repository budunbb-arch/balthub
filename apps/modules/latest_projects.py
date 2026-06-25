# latest_projects.py
from django.conf import settings
from django.core.cache import cache
from apps.estates.projects.models import Project

def get_latest_projects(request):
    cache_key = "latest_projects"
    projects = cache.get(cache_key)
    if projects is None:
        projects = list(
            Project.objects
            .active()
            .select_related("developer", "params__city")
            .prefetch_related("images")
            .order_by("-id")[:8]
        )
        cache.set(cache_key, projects, settings.CACHE_TTL)
    return {"latest_projects": projects}
