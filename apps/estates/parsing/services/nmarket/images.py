# /opt/balthub/apps/estates/parsing/services/nmarket/import_images.py

from pathlib import Path
from django.conf import settings
from urllib.request import Request, urlopen
from urllib.parse import unquote, urlparse
from PIL import Image, ImageOps

import hashlib
import mimetypes
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


IMAGE_VARIANTS: dict[str, list[tuple[int, int | None]]] = {

    # (width, height)
    # height=None -> сохранить пропорции

    "flat_plans": [
        (480, None),
    ],
    "house_plans": [
        (800, 600),
        (200, 150),
    ],
    "houses": [
        (480, 640),
        (800, 600),
    ],
    "project_images": [
        (480, 640),
        (800, 600),
        (1200, 600),
        (200, 150),
    ],
}

MAX_WORKERS = 10


def normalize_image_url(url):
    """Нормализовать URL: убрать пробелы, добавить https: если без схемы.
    Должно совпадать с нормализацией в _collect_images (importer.py)."""
    if not url:
        return None
    normalized_url = url.strip()
    if normalized_url.startswith("//"):
        normalized_url = "https:" + normalized_url
    if not normalized_url.lower().startswith(("http://", "https://")):
        return None
    return normalized_url


def _download_single_image(url, subfolder):
    """Скачать одно изображение, сохранить оригинал. Вернуть media URL или None."""
    normalized_url = normalize_image_url(url)
    if not normalized_url:
        return None

    media_root = Path(settings.MEDIA_ROOT)
    target_dir = media_root / "imported_images" / subfolder
    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        request = Request(normalized_url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=20) as response:
            if getattr(response, "status", 200) != 200:
                return None

            content = response.read()
            if not content:
                return None

            parsed = urlparse(normalized_url)
            basename = Path(unquote(parsed.path)).name
            ext = Path(basename).suffix.lower()
            if not ext or len(ext) > 5:
                content_type = response.headers.get("Content-Type", "")
                ext = mimetypes.guess_extension(content_type.split(";")[0].strip() or "") or ".jpg"

            file_hash = hashlib.md5(content).hexdigest()
            filename = f"{file_hash}{ext}"
            target_path = target_dir / filename

            if not target_path.exists():
                target_path.write_bytes(content)

            return f"{settings.MEDIA_URL.rstrip('/')}/{Path('imported_images') / subfolder / filename}"
    except Exception as exc:
        logger.warning(
            "Image download failed: %s (%s)",
            normalized_url,
            exc
        )
        return None


def download_images(urls, subfolder):
    """Параллельно скачать список URL изображений.
    Возвращает словарь {нормализованный_url: media_url} для успешно скачанных."""
    if not urls:
        return {}

    # Нормализовать все URL для единообразия
    normalized_urls = []
    for url in urls:
        n = normalize_image_url(url)
        if n:
            normalized_urls.append(n)

    # Убрать дубли
    unique_urls = list(dict.fromkeys(normalized_urls))

    result_map = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_map = {
            executor.submit(_download_single_image, url, subfolder): url
            for url in unique_urls
        }
        for future in as_completed(future_map):
            original_url = future_map[future]
            try:
                media_url = future.result()
                if media_url:
                    result_map[original_url] = media_url
            except Exception:
                pass

    return result_map


def download_image(url, subfolder):
    """Одиночная загрузка (для совместимости, но лучше использовать download_images)."""
    if not url:
        return None
    normalized_url = normalize_image_url(url)
    if not normalized_url:
        return None
    return _download_single_image(normalized_url, subfolder)


def generate_all_variants():
    """Сгенерировать variants для всех скачанных изображений.
    Вызывать однократно после цикла импорта."""
    media_root = Path(settings.MEDIA_ROOT)
    imported_root = media_root / "imported_images"

    if not imported_root.exists():
        return

    for subfolder in IMAGE_VARIANTS:
        subfolder_path = imported_root / subfolder
        if not subfolder_path.exists():
            continue
        for img_path in subfolder_path.iterdir():
            if img_path.is_file() and img_path.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
                # Проверить, что это не вариант (не содержит _crop_ или _auto)
                name = img_path.stem
                if not any(marker in name for marker in ("_crop_", "_auto", "xauto")):
                    generate_image_variants(img_path, subfolder)


def generate_image_variants(original_path, subfolder):
    """Создаёт копии изображений разных размеров и кэширует их на диске."""
    variants = IMAGE_VARIANTS.get(subfolder, [])

    for width, height in variants:
        save_image_variant(original_path, width, height)


def save_image_variant(original_path, width, height=None):
    """Сохраняет одну уменьшенную версию изображения."""
    try:
        image = Image.open(original_path)
        image = ImageOps.exif_transpose(image)
        image_format = image.format or "JPEG"

        if height is None:
            max_size = (width, 10000)
            image.thumbnail(max_size, Image.LANCZOS)
        else:
            image = ImageOps.fit(
                image,
                (width, height),
                Image.LANCZOS
            )

        if image.mode in ("RGBA", "LA"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[3])
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")

        base_name = original_path.stem
        ext = original_path.suffix.lower() or ".jpg"
        if height is None:
            size_suffix = f"{width}xauto"
        else:
            size_suffix = f"crop_{width}x{height}"
        variant_path = original_path.with_name(f"{base_name}_{size_suffix}{ext}")

        if variant_path.exists():
            return

        image.save(
            variant_path,
            format=image_format,
            quality=100,
            optimize=True,
        )
    except Exception as exc:
        logger.exception(
            "Failed to create image variant for %s",
            original_path,
        )


def save_image_crop_variant(original_path, width):
    target_height = int(width * 4 / 3)

    with Image.open(original_path) as image:
        image = ImageOps.exif_transpose(image)
        cropped = ImageOps.fit(
            image,
            (width, target_height),
            Image.LANCZOS,
            centering=(0.5, 0.5)
        )

        if cropped.mode in ("RGBA", "LA"):
            background = Image.new("RGB", cropped.size, (255, 255, 255))
            background.paste(cropped, mask=cropped.split()[3])
            cropped = background
        elif cropped.mode != "RGB":
            cropped = cropped.convert("RGB")

        base = original_path.stem
        ext = original_path.suffix.lower() or ".jpg"
        variant_path = original_path.with_name(f"{base}_crop_{width}x{target_height}{ext}")

        if not variant_path.exists():
            cropped.save(variant_path, quality=85, optimize=True)