# apps/estates/parsing/services/nmarket/helpers.py

def get_text(parent, path, ns):
    el = parent.find(path, ns)
    return el.text.strip() if el is not None and el.text else None

def get_nested_text(parent, path, ns):
    el = parent.find(path, ns)
    return el.text.strip() if el is not None and el.text else None

def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

def to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def update_instance(instance, **fields):
    changed_fields = []

    for field, value in fields.items():
        if getattr(instance, field) != value:
            setattr(instance, field, value)
            changed_fields.append(field)

    return changed_fields


def pick_downloaded(url, download_map):
    """Вернуть локальный media URL, если изображение было скачано, иначе None.
    download_map — словарь {исходный_url: media_url} из download_images.
    URL ожидается уже нормализованным (из _collect_images)."""
    if not url or not download_map:
        return None
    return download_map.get(url)


def pick_downloaded_list(urls, download_map):
    """Вернуть список локальных media URL для успешно скачанных изображений.
    download_map — словарь {исходный_url: media_url} из download_images.
    URL ожидаются уже нормализованными (из _collect_images)."""
    if not urls or not download_map:
        return []
    result = []
    for url in urls:
        if not url:
            continue
        media_url = download_map.get(url)
        if media_url:
            result.append(media_url)
    return result


class BulkUpdater:

    def __init__(self):
        self.data = {}

    def add(self, obj, fields):

        if not fields:
            return

        model = obj.__class__

        bucket = self.data.setdefault(model, [])

        bucket.append((obj, tuple(sorted(fields))))

    def flush(self):

        from collections import defaultdict

        for model, objects in self.data.items():

            by_fields = defaultdict(list)

            for obj, fields in objects:
                by_fields[fields].append(obj)

            for fields, objs in by_fields.items():
                model.objects.bulk_update(
                    objs,
                    list(fields),
                    batch_size=500,
                )

        self.data.clear()