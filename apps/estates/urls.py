# apps/estates/urls.py

from django.urls import path, include
from apps.estates.projects.views import project_list, project_detail
from apps.estates.houses.views import house_list, house_detail, house_plans_ajax, plans, plans_ajax
from apps.estates.flats.views import flat_detail
from apps.estates.search.views import search_results
from apps.estates.developers.views import developer_list, developer_detail
from apps.estates.tags.urls import urlpatterns as tags_urlpatterns

urlpatterns = [
    # AJAX
    path(
        "ajax/house/<slug:house_slug>/plans/",
        house_plans_ajax,
        name="house_plans_ajax"
    ),
    path("ajax/plans/", plans_ajax, name="plans_ajax"),

    # списки
    path("projects/", project_list, name="project_list"),
    path("houses/", house_list, name="house_list"),
    path("plans/", plans, name="plans"),
    path("developers/", developer_list, name="developer_list"),

    path("developers/<slug:slug>/", developer_detail, name="developer_detail"),

    path("search/", search_results, name="search_results"),

    # иерархия
    path("projects/<slug:project_slug>/", project_detail, name="project_detail"),
    path("projects/<slug:project_slug>/<slug:house_slug>/", house_detail, name="house_detail"),
    path("projects/<slug:project_slug>/<slug:house_slug>/<slug:flat_slug>/", flat_detail, name="flat_detail"),

    # теги
    path("tags/", include((tags_urlpatterns, "tags"))),
]
