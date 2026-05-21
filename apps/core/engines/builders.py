def build_seo(request, context=None):

    resolver = request.resolver_match

    if not resolver:
        return {}

    view = resolver.url_name
    context = context or {}

    seo = {
        "title": "Balthub",
        "description": "",
        "keywords": "",
        "h1": "",
    }

    # =====================================================
    # PROJECT DETAIL
    # =====================================================

    if view == "project_detail":

        project = context.get("project")

        if project:
            seo["title"] = f"{project.name} — квартиры и цены"
            seo["h1"] = project.name
            seo["description"] = (
                f"Квартиры в ЖК {project.name}. "
                f"Планировки, цены, дома, инфраструктура."
            )

    # =====================================================
    # HOUSE DETAIL
    # =====================================================

    elif view == "house_detail":

        house = context.get("house")

        if house:
            seo["title"] = f"Дом #{house.id}"
            seo["h1"] = f"Дом #{house.id}"

    # =====================================================
    # FLAT DETAIL
    # =====================================================

    elif view == "flat_detail":

        flat = context.get("flat")

        if flat:
            seo["title"] = (
                f"Квартира {flat.number} "
                f"в {flat.house.project.name}"
            )

            seo["h1"] = f"Квартира {flat.number}"

    return seo