from apps.core.models import SiteSettings


def build_seo(request, context=None):
    resolver = request.resolver_match

    if not resolver:
        return {}

    view = resolver.url_name
    context = context or {}

    site_settings = SiteSettings.get_solo()
    default_title = site_settings.default_title if site_settings and site_settings.default_title else (site_settings.site_name if site_settings else "Balthub")
    default_description = site_settings.default_description if site_settings else ""
    default_keywords = site_settings.default_keywords if site_settings else ""
    default_canonical = site_settings.default_canonical if site_settings and site_settings.default_canonical else request.build_absolute_uri()
    default_robots = site_settings.default_robots if site_settings else "index, follow"

    seo = {
        "title": default_title,
        "description": default_description,
        "keywords": default_keywords,
        "h1": "",
        "canonical": default_canonical,
        "robots": default_robots,
    }

    def pick_value(primary, fallback=None):
        return primary or fallback or ""

    def build_robots(obj):
        if not obj:
            return "index, follow"

        index = "index" if getattr(obj, "robots_index", True) else "noindex"
        follow = "follow" if getattr(obj, "robots_follow", True) else "nofollow"
        return f"{index}, {follow}"

    if view == "project_detail":
        project = context.get("project")

        if project:
            seo["title"] = pick_value(project.meta_title, default_title)
            seo["description"] = pick_value(project.meta_description, default_description)
            seo["keywords"] = pick_value(project.meta_keywords, default_keywords)
            seo["h1"] = pick_value(project.seo_h1, project.name)
            seo["canonical"] = pick_value(
                project.canonical_url,
                request.build_absolute_uri()
            )
            seo["robots"] = build_robots(project)

    elif view == "house_detail":
        house = context.get("house")

        if house:
            seo["title"] = pick_value(house.meta_title, default_title)
            seo["description"] = pick_value(house.meta_description, default_description)
            seo["keywords"] = pick_value(house.meta_keywords, default_keywords)
            seo["h1"] = pick_value(
                house.seo_h1,
                getattr(house.params, "address", f"Дом #{house.id}")
            )
            seo["canonical"] = pick_value(
                house.canonical_url,
                request.build_absolute_uri()
            )
            seo["robots"] = build_robots(house)

    elif view == "flat_detail":
        flat = context.get("flat")

        if flat:
            seo["title"] = pick_value(flat.meta_title, default_title)
            seo["description"] = pick_value(flat.meta_description, default_description)
            seo["keywords"] = pick_value(flat.meta_keywords, default_keywords)
            seo["h1"] = pick_value(flat.seo_h1, f"Квартира {flat.number}")
            seo["canonical"] = pick_value(
                flat.canonical_url,
                request.build_absolute_uri()
            )
            seo["robots"] = build_robots(flat)

    elif view == "developer_detail":
        developer = context.get("developer")

        if developer:
            seo["title"] = pick_value(developer.meta_title, default_title)
            seo["description"] = pick_value(developer.meta_description, default_description)
            seo["keywords"] = pick_value(developer.meta_keywords, default_keywords)
            seo["h1"] = pick_value(developer.seo_h1, developer.name)
            seo["canonical"] = pick_value(
                developer.canonical_url,
                request.build_absolute_uri()
            )
            seo["robots"] = build_robots(developer)

    return seo
