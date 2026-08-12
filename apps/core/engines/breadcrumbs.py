from django.urls import reverse, Resolver404, resolve

from apps.estates.projects.models import Project
from apps.estates.houses.models import House
from apps.estates.flats.models import Flat
from apps.estates.developers.models import Developer
from apps.estates.tags.models import Tag
from apps.core.documents.models import Document

import logging

logger = logging.getLogger(__name__)


def build_breadcrumbs(request):

    resolver = request.resolver_match

    if not resolver:
        return []

    view = resolver.url_name

    if view == "home":
        return []

    breadcrumbs = [
        {
            "title": "Главная",
            "url": reverse("home"),
        }
    ]

    try:
        # =====================================================
        # DEVELOPERS LIST
        # =====================================================

        if view == "developer_list":

            breadcrumbs.append({
                "title": "Застройщики",
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
                "title": "Застройщики",
                "url": reverse("developer_list"),
            })

            breadcrumbs.append({
                "title": developer.name if developer else developer_slug,
                "url": None,
            })


        # =====================================================
        # PROJECT LIST
        # =====================================================

        elif view == "project_list":

            breadcrumbs.append({
                "title": "Новостройки",
                "url": None,
            })

        # =====================================================
        # PROJECT DETAIL
        # =====================================================

        elif view == "project_detail":

            project_slug = resolver.kwargs.get("project_slug")

            project = (
                Project.objects
                .only("name", "slug")
                .filter(slug=project_slug)
                .first()
            )

            breadcrumbs.append({
                "title": "Новостройки",
                "url": reverse("project_list"),
            })

            breadcrumbs.append({
                "title": project.name if project else project_slug,
                "url": None,
            })


        # =====================================================
        # HOUSE LIST
        # =====================================================

        elif view == "house_list":

            breadcrumbs.append({
                "title": "Дома",
                "url": None,
            })


        # =====================================================
        # PLANS LIST
        # =====================================================

        elif view == "plans":

            breadcrumbs.append({
                "title": "Планировки",
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
                .only("name", "slug")
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
                "title": "Новостройки",
                "url": reverse("project_list"),
            })

            if project:
                breadcrumbs.append({
                    "title": project.name,
                    "url": reverse(
                        "project_detail",
                        kwargs={
                            "project_slug": project.slug
                        }
                    ),
                })

            if house:
                breadcrumbs.append({
                    "title": f"Дом #{house.id}",
                    "url": reverse(
                        "house_detail",
                        kwargs={
                            "project_slug": project.slug,
                            "house_slug": house.slug,
                        }
                    ),
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
                .only("name", "slug")
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
                "title": "Новостройки",
                "url": reverse("project_list"),
            })

            if project:
                breadcrumbs.append({
                    "title": project.name,
                    "url": reverse(
                        "project_detail",
                        kwargs={
                            "project_slug": project.slug
                        }
                    ),
                })

            if house:
                breadcrumbs.append({
                    "title": f"Дом #{house.id}",
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
                    f"Квартира {flat.number}"
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
                "title": "Документы",
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
                "title": "Документы",
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
                "title": "Теги",
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
                "title": "Теги",
                "url": reverse("tags:tag_list"),
            })

            breadcrumbs.append({
                "title": tag.name if tag else tag_slug,
                "url": None,
            })

    except Exception:
        logger.exception("BREADCRUMB ERROR")

    return breadcrumbs
