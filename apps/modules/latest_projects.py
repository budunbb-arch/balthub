# /opt/balthub/apps/modules/latest_projects.py

from apps.estates.projects.models import Project


# apps/modules/latest_projects.py

MODULE = "default/modules/latest_projects.html"


def get_context(request, module):
    projects = list(
        Project.objects
        .active()
        .select_related("developer", "params__city")
        .prefetch_related("images")
        .order_by("-id")[:8]
    )
    return {"latest_projects": projects}