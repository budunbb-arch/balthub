from django.urls import reverse, Resolver404, resolve

from apps.core.dictionaries.models import City
from apps.estates.projects.models import Project
from apps.estates.houses.models import House
from apps.estates.flats.models import Flat
from apps.estates.developers.models import Developer
from apps.estates.tags.models import Tag
from apps.core.documents.models import Document
from apps.core.localization import t

import logging

logger = logging.getLogger(__name__)


def _project_breadcrumb_title(project):
    project_type_alias = (
        project.project_type.project_type_alias
        if project.project_type
        else ""
    )
    return f"{project_type_alias} «{project.name}»".strip()


def build_breadcrumbs(request):

    resolver = request.resolver_match

    if not resolver:
        return []

    view = resolver.url_name

    if view == "home":
        return []

    breadcrumbs = [
        {
            "title": t("text_homepage"),
            "url": reverse("home"),
        }
    ]

    try:
        # =====================================================
        # DEVELOPERS LIST
        # =====================================================

        if view == "developer_list":

            breadcrumbs.append({
                "title": t("text_developers"),
                "url": None,
            })

        # =====================================================
        # DEVELOPER DETAIL
        # =====================================================

        elif view == "developer_detail":

            developer_slug = resolver.kwargs.get("slug")

            developer = (
                Developer.objects
                .only("name", "slug")
                .filter(slug=developer_slug)
                .first()
            )

            breadcrumbs.append({
                "title": t("text_developers"),
                "url": reverse("developer_list"),
            })

            breadcrumbs.append({
                "title": developer.name if developer else developer_slug,
                "url": None,
            })


        # =====================================================
        # SEARCH RESULTS
        # =====================================================

        elif view == "search_results":

            breadcrumbs.append({
                "title": t("search_title"),
                "url": None,
            })

        # =====================================================
        # FEEDBACK PAGE
        # =====================================================

        elif view == "feedback_page":

            breadcrumbs.append({
                "title": t("feedback_page"),
                "url": None,
            })

        # =====================================================
        # PROJECT LIST
        # =====================================================

        elif view == "project_list":

            breadcrumbs.append({
                "title": t("text_newprojects"),
                "url": None,
            })

        elif view == "geography_list":

            breadcrumbs.append({
                "title": t("text_geography"),
                "url": None,
            })

        elif view == "geography_detail":

            city = getattr(request, "geo_city", None)
            if city is None:
                city = (
                    City.objects
                    .only("name")
                    .filter(slug=resolver.kwargs.get("city_slug"))
                    .first()
                )

            breadcrumbs.append({
                "title": t("text_geography"),
                "url": reverse("geography_list"),
            })
            if city:
                breadcrumbs.append({
                    "title": city.name,
                    "url": None,
                })

        # =====================================================
        # PROJECT DETAIL
        # =====================================================

        elif view == "project_detail":

            project_slug = resolver.kwargs.get("project_slug")

            project = (
                Project.objects
                .only("name", "slug", "project_type__project_type_alias")
                .select_related("project_type")
                .filter(slug=project_slug)
                .first()
            )

            breadcrumbs.append({
                "title": t("text_newprojects"),
                "url": reverse("project_list"),
            })

            breadcrumbs.append({
                "title": (
                    _project_breadcrumb_title(project)
                    if project
                    else project_slug
                ),
                "url": None,
            })


        # =====================================================
        # HOUSE LIST
        # =====================================================

        elif view == "house_list":

            breadcrumbs.append({
                "title": t("text_houses"),
                "url": None,
            })


        # =====================================================
        # PLANS LIST
        # =====================================================

        elif view == "plans":

            breadcrumbs.append({
                "title": t("text_layouts"),
                "url": None,
            })


        # =====================================================
        # HOUSE DETAIL
        # =====================================================

        elif view == "house_detail":

            project_slug = resolver.kwargs.get("project_slug")
            house_slug = resolver.kwargs.get("house_slug")

            project = (
                Project.objects
                .only("name", "slug", "project_type__project_type_alias")
                .select_related("project_type")
                .filter(slug=project_slug)
                .first()
            )

            house = (
                House.objects
                .only("id", "slug", "project")
                .filter(slug=house_slug)
                .select_related("project")
                .first()
            )

            breadcrumbs.append({
                "title": t("text_newprojects"),
                "url": reverse("project_list"),
            })

            if project:
                breadcrumbs.append({
                    "title": _project_breadcrumb_title(project),
                    "url": reverse(
                        "project_detail",
                        kwargs={
                            "project_slug": project.slug
                        }
                    ),
                })

            if house:
                breadcrumbs.append({
                    "title": f"{house.params.corpus}",
                    "url": None,
                })


        # =====================================================
        # FLAT DETAIL
        # =====================================================

        elif view == "flat_detail":

            project_slug = resolver.kwargs.get("project_slug")
            house_slug = resolver.kwargs.get("house_slug")
            flat_slug = resolver.kwargs.get("flat_slug")

            project = (
                Project.objects
                .only("name", "slug", "project_type__project_type_alias")
                .select_related("project_type")
                .filter(slug=project_slug)
                .first()
            )

            house = (
                House.objects
                .only("id", "slug", "project")
                .filter(slug=house_slug)
                .select_related("project")
                .first()
            )

            flat = (
                Flat.objects
                .only("number", "slug")
                .filter(slug=flat_slug)
                .first()
            )

            breadcrumbs.append({
                "title": t("text_newprojects"),
                "url": reverse("project_list"),
            })

            if project:
                breadcrumbs.append({
                    "title": _project_breadcrumb_title(project),
                    "url": reverse(
                        "project_detail",
                        kwargs={
                            "project_slug": project.slug
                        }
                    ),
                })

            if house:
                breadcrumbs.append({
                    "title": f"{house.params.corpus}",
                    "url": reverse(
                        "house_detail",
                        kwargs={
                            "project_slug": project.slug,
                            "house_slug": house.slug,
                        }
                    ),
                })

            breadcrumbs.append({
                "title": (
                    f'{t("text_flat")} {flat.number}'
                    if flat and flat.number
                    else flat_slug
                ),
                "url": None,
            })

        # =====================================================
        # DOCUMENTS LIST
        # =====================================================

        elif view == "documents":
            breadcrumbs.append({
                "title": t("text_documents"),
                "url": None,
            })

        # =====================================================
        # DOCUMENT DETAIL
        # =====================================================

        elif view == "document_detail":
            document_id = resolver.kwargs.get("document_id")
            document = (
                Document.objects
                .only("id", "document_name")
                .filter(pk=document_id)
                .first()
            )

            breadcrumbs.append({
                "title": t("text_documents"),
                "url": reverse("documents"),
            })

            breadcrumbs.append({
                "title": document.document_name if document else f"#{document_id}",
                "url": None,
            })

        # =====================================================
        # TAGS LIST
        # =====================================================

        elif view in ("tag_list", "tags:tag_list"):
            breadcrumbs.append({
                "title": t("text_tags"),
                "url": None,
            })

        # =====================================================
        # TAG DETAIL
        # =====================================================

        elif view in ("tag_detail", "tags:tag_detail"):
            tag_slug = resolver.kwargs.get("tag_slug")
            tag = None
            try:
                tag = (
                    Tag.objects
                    .only("name", "slug")
                    .filter(slug=tag_slug)
                    .first()
                )
            except Exception:
                logger.exception("BREADCRUMB TAG ERROR")

            breadcrumbs.append({
                "title": t("text_tags"),
                "url": reverse("tags:tag_list"),
            })

            breadcrumbs.append({
                "title": tag.name if tag else tag_slug,
                "url": None,
            })

    except Exception:
        logger.exception("BREADCRUMB ERROR")

    return breadcrumbs
