# /opt/balthub/apps/core/pagination.py

from django.core.paginator import (
    Paginator,
    EmptyPage,
    PageNotAnInteger,
)


def build_page_range(page_obj, radius=1):
    """
    Строит pagination window:

    1 2 ... 8 9 10 ... 57

    radius=1:
    текущая ±1 страница
    """

    current = page_obj.number
    total = page_obj.paginator.num_pages

    pages = []

    # первые страницы
    pages.extend([1, 2])

    # окно вокруг текущей
    for num in range(current - radius, current + radius + 1):
        if 1 <= num <= total:
            pages.append(num)

    # последние страницы
    pages.extend([total - 1, total])

    # cleanup
    pages = sorted(set(pages))

    final = []
    prev = None

    for num in pages:

        if prev and num - prev > 1:
            final.append("...")

        final.append(num)
        prev = num

    return final


def paginate_queryset(request, queryset, per_page=10):

    page = request.GET.get("page", 1)

    paginator = Paginator(queryset, per_page)

    try:
        page_obj = paginator.page(page)

    except PageNotAnInteger:
        page_obj = paginator.page(1)

    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    page_range = build_page_range(page_obj)

    return page_obj, paginator, page_range