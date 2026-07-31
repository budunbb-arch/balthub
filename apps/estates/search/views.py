# /opt/balthub/apps/estates/search/views.py

from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Q
from apps.estates.projects.models import Project
from apps.estates.houses.models import House
from apps.estates.flats.models import Flat, FlatParams
from apps.estates.developers.models import Developer


def search_results(request):
    query = (request.GET.get("q") or "").strip()
    city_id = request.GET.get("city")
    district_id = request.GET.get("district")
    property_type_id = request.GET.get("property_type")
    rooms_alias = request.GET.get("rooms_alias")
    price_band = request.GET.get("price_band")

    def _to_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    # Ограничиваем rooms_alias валидными значениями
    valid_rooms_aliases = set(
        FlatParams.objects.exclude(rooms_alias__isnull=True)
        .exclude(rooms_alias__exact="")
        .values_list("rooms_alias", flat=True)
    )
    if rooms_alias not in valid_rooms_aliases:
        rooms_alias = None

    city_id = _to_int(city_id)
    district_id = _to_int(district_id)
    property_type_id = _to_int(property_type_id)

    # Валидируем price_band: только если обе части - числа
    def _validate_price_band(value):
        if not value or "-" not in value:
            return None
        parts = value.split("-", 1)
        if len(parts) != 2:
            return None
        min_str, max_str = parts[0], parts[1]
        try:
            float(min_str)
            float(max_str)
            return value
        except (ValueError, TypeError):
            return None

    price_band = _validate_price_band(price_band)

    # Получаем читаемые названия для фильтров
    city_name = ""
    if city_id:
        from apps.core.dictionaries.models import City
        try:
            city_name = City.objects.get(id=city_id).name
        except City.DoesNotExist:
            city_name = str(city_id)

    district_name = ""
    if district_id:
        from apps.core.dictionaries.models import District
        try:
            district_name = District.objects.get(id=district_id).name
        except District.DoesNotExist:
            district_name = str(district_id)

    property_type_name = ""
    if property_type_id:
        from apps.core.dictionaries.models import PropertyType
        try:
            property_type_name = PropertyType.objects.get(id=property_type_id).name
        except PropertyType.DoesNotExist:
            property_type_name = str(property_type_id)

    base_q = Q(house__project__is_public=True, house__project__is_deleted=False)

    text_q = Q()
    if query:
        text_q = (
            Q(house__project__name__icontains=query) |
            Q(house__project__description__description__icontains=query) |
            Q(house__params__address__icontains=query) |
            Q(house__project__developer__name__icontains=query) |
            Q(number__icontains=query)
        )

    filter_q = Q()
    if city_id:
        filter_q &= Q(house__project__params__city_id=city_id)
    if district_id:
        filter_q &= Q(house__project__params__district_id=district_id)
    if property_type_id:
        filter_q &= Q(house__project__params__property_type_id=property_type_id)
    if rooms_alias:
        filter_q &= Q(params__rooms_alias=rooms_alias)

    price_q = Q()
    if price_band and "-" in price_band:
        parts = price_band.split("-", 1)
        min_str, max_str = parts[0], parts[1]
        if min_str:
            try:
                price_q &= Q(deals__price__gte=float(min_str))
            except (ValueError, TypeError):
                pass
        if max_str and max_str not in ("", "None"):
            try:
                price_q &= Q(deals__price__lte=float(max_str))
            except (ValueError, TypeError):
                pass

    qs = base_q & text_q & filter_q & price_q

    project_q = Q(is_public=True, is_deleted=False)

    if query:
        project_q &= Q(name__icontains=query) | Q(developer__name__icontains=query)

    if city_id:
        project_q &= Q(params__city_id=city_id)

    if district_id:
        project_q &= Q(params__district_id=district_id)

    if property_type_id:
        project_q &= Q(params__property_type_id=property_type_id)

    projects_qs = Project.objects.filter(project_q).distinct().select_related(
        "params__city", "params__district", "developer"
    )

    # Дополнительно фильтруем проекты через квартиры, если заданы rooms_alias или price_band
    if rooms_alias or price_band:
        flat_q = Q()
        if rooms_alias:
            flat_q &= Q(params__rooms_alias=rooms_alias)
        if price_band and "-" in price_band:
            parts = price_band.split("-", 1)
            min_str, max_str = parts[0], parts[1]
            if min_str:
                try:
                    flat_q &= Q(deals__price__gte=float(min_str))
                except (ValueError, TypeError):
                    pass
            if max_str and max_str not in ("", "None"):
                try:
                    flat_q &= Q(deals__price__lte=float(max_str))
                except (ValueError, TypeError):
                    pass

        projects_with_flats = Flat.objects.filter(
            flat_q,
            house__project__in=projects_qs,
            house__project__is_public=True,
            house__project__is_deleted=False,
        ).values_list("house__project_id", flat=True)

        projects_qs = projects_qs.filter(id__in=projects_with_flats)

    # Собираем единый список результатов с типом (без квартир и застройщиков)
    results = []
    results.extend([("project", p) for p in projects_qs])

    page_number = request.GET.get("page")
    paginator = Paginator(results, 12)
    results_page = paginator.get_page(page_number)

    context = {
        "results": results_page,
        "paginator": paginator,
        "query": query,
        "city_id": city_id,
        "city_name": city_name,
        "district_id": district_id,
        "district_name": district_name,
        "property_type_id": property_type_id,
        "property_type_name": property_type_name,
        "rooms_alias": rooms_alias,
        "price_band": price_band,
        "projects": results_page,
    }

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render(
            request,
            "default/pages/search/ajax/_results_list.html",
            context,
        )

    return render(request, "default/pages/search.html", context)
