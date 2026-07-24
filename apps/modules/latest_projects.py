# latest_projects.py
from apps.estates.projects.models import Project


def get_latest_projects(request):
    projects = list(
        Project.objects
        .active()
        .select_related("developer", "params__city")
        .prefetch_related("images")
        .order_by("-id")[:8]
    )
    return {"latest_projects": projects}