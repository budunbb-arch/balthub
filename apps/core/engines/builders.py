from apps.core.models import SiteSettings

import json
import logging

logger = logging.getLogger(__name__)


def get_default_seo(request):
    site_settings = SiteSettings.get_solo()

    default_sitename = site_settings.site_name 
    default_title = site_settings.default_title
    default_description = site_settings.default_description if site_settings else ""
    default_keywords = site_settings.default_keywords if site_settings else ""
    default_canonical = site_settings.default_canonical if site_settings and site_settings.default_canonical else request.build_absolute_uri()
    default_robots = site_settings.default_robots if site_settings else "index, follow"

    return {
        "title": default_title,
        "description": default_description,
        "keywords": default_keywords,
        "h1": "",
        "canonical": default_canonical,
        "robots": default_robots,
        "og_title": (
            f"{default_sitename} - {default_title}"
            if default_sitename and default_title
            else (default_sitename or default_title)
        ),
        "og_description": default_description,
        "og_image": "",
        "og_url": default_canonical,
        "json_ld": {},
        "site_name": default_sitename,
        "site_title": default_title,
    }


def build_seo(request, context=None):
    view = getattr(request, "view_name", None)
    context = context or {}

    if not view:
        return get_default_seo(request)

    def pick_value(primary, fallback=None):
        return primary or fallback or ""

    def build_robots(obj):
        if not obj:
            return "index, follow"

        index = "index" if getattr(obj, "robots_index", True) else "noindex"
        follow = "follow" if getattr(obj, "robots_follow", True) else "nofollow"
        return f"{index}, {follow}"

    def build_og_image(obj):
        if not obj:
            return ""
        images = getattr(obj, "images", None)
        if images:
            try:
                first = images.first()
                if first:
                    return first.image.url if hasattr(first, "image") else ""
            except Exception:
                pass
        return ""

    def build_json_ld(obj_type, obj):
        if not obj:
            return {}

        base = {
            "@context": "https://schema.org",
            "@type": obj_type,
            "name": getattr(obj, "name", ""),
            "url": getattr(obj, "canonical_url", "") or request.build_absolute_uri(),
        }

        if hasattr(obj, "meta_description") and obj.meta_description:
            base["description"] = obj.meta_description

        image = build_og_image(obj)
        if image:
            base["image"] = image

        return base

    seo = get_default_seo(request)

    if view == "project_detail":
        project = getattr(request, "project", None)

        if project:
            seo["title"] = pick_value(project.meta_title, seo["title"])
            seo["description"] = pick_value(project.meta_description, seo["description"])
            seo["keywords"] = pick_value(project.meta_keywords, seo["keywords"])
            seo["h1"] = pick_value(project.seo_h1, project.name)
            seo["canonical"] = pick_value(
                project.canonical_url,
                request.build_absolute_uri()
            )
            seo["robots"] = build_robots(project)
            seo["og_title"] = f"{seo['title']} - {seo['site_name']} - {seo['site_title']}"
            seo["og_description"] = seo["description"]
            seo["og_image"] = build_og_image(project)
            seo["og_url"] = seo["canonical"]
            seo["json_ld"] = json.dumps(build_json_ld("ApartmentComplex", project), ensure_ascii=False)

    elif view == "house_detail":
        house = context.get("house")

        if house:
            seo["title"] = pick_value(house.meta_title, seo["title"])
            seo["description"] = pick_value(house.meta_description, seo["description"])
            seo["keywords"] = pick_value(house.meta_keywords, seo["keywords"])
            seo["h1"] = pick_value(
                house.seo_h1,
                getattr(house.params, "address", f"Дом #{house.id}")
            )
            seo["canonical"] = pick_value(
                house.canonical_url,
                request.build_absolute_uri()
            )
            seo["robots"] = build_robots(house)
            seo["og_title"] = seo["title"]
            seo["og_description"] = seo["description"]
            seo["og_image"] = build_og_image(house)
            seo["og_url"] = seo["canonical"]
            seo["json_ld"] = json.dumps(build_json_ld("Residence", house), ensure_ascii=False)

    elif view == "flat_detail":
        flat = context.get("flat")

        if flat:
            seo["title"] = pick_value(flat.meta_title, seo["title"])
            seo["description"] = pick_value(flat.meta_description, seo["description"])
            seo["keywords"] = pick_value(flat.meta_keywords, seo["keywords"])
            seo["h1"] = pick_value(flat.seo_h1, f"Квартира {flat.number}")
            seo["canonical"] = pick_value(
                flat.canonical_url,
                request.build_absolute_uri()
            )
            seo["robots"] = build_robots(flat)
            seo["og_title"] = seo["title"]
            seo["og_description"] = seo["description"]
            seo["og_image"] = build_og_image(flat)
            seo["og_url"] = seo["canonical"]
            seo["json_ld"] = json.dumps(build_json_ld("Apartment", flat), ensure_ascii=False)

    elif view == "developer_detail":
        developer = context.get("developer")

        if developer:
            seo["title"] = pick_value(developer.meta_title, seo["title"])
            seo["description"] = pick_value(developer.meta_description, seo["description"])
            seo["keywords"] = pick_value(developer.meta_keywords, seo["keywords"])
            seo["h1"] = pick_value(developer.seo_h1, developer.name)
            seo["canonical"] = pick_value(
                developer.canonical_url,
                request.build_absolute_uri()
            )
            seo["robots"] = build_robots(developer)
            seo["og_title"] = seo["title"]
            seo["og_description"] = seo["description"]
            seo["og_image"] = build_og_image(developer)
            seo["og_url"] = seo["canonical"]
            seo["json_ld"] = json.dumps(build_json_ld("HomeAndConstructionBusiness", developer), ensure_ascii=False)

    elif view == "tag_detail":
        tag = context.get("tag")

        if tag:
            seo["title"] = pick_value(tag.meta_title, seo["title"])
            seo["description"] = pick_value(tag.meta_description, seo["description"])
            seo["keywords"] = pick_value(tag.meta_keywords, seo["keywords"])
            seo["h1"] = pick_value(tag.seo_h1, tag.name)
            seo["canonical"] = pick_value(
                tag.canonical_url,
                request.build_absolute_uri()
            )
            seo["robots"] = build_robots(tag)
            seo["og_title"] = seo["title"]
            seo["og_description"] = seo["description"]
            seo["og_image"] = build_og_image(tag)
            seo["og_url"] = seo["canonical"]
            seo["json_ld"] = json.dumps(build_json_ld("Thing", tag), ensure_ascii=False)

    return seo
