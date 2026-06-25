from glob import glob
from urllib.parse import urlparse
import os

from django import template
from django.conf import settings

register = template.Library()


def _url_to_fs_path(url):
    if not url:
        return None
    parsed = urlparse(url)
    path = parsed.path
    media_url = settings.MEDIA_URL
    if path.startswith(media_url):
        rel = path[len(media_url):].lstrip("/")
    else:
        # try with leading slash
        rel = path.lstrip("/")
    return os.path.join(settings.MEDIA_ROOT, rel)


def _fs_path_to_url(fs_path):
    # convert absolute fs path under MEDIA_ROOT back to URL
    try:
        rel = os.path.relpath(fs_path, settings.MEDIA_ROOT)
    except Exception:
        return None
    return settings.MEDIA_URL.rstrip("/") + "/" + rel.replace(os.path.sep, "/")


@register.filter
def image_variant(image_url, width):
    """Return URL of image variant (e.g. original_640xauto.jpg) if exists, else original."""
    if not image_url:
        return ""

    fs_path = _url_to_fs_path(image_url)
    if not fs_path or not os.path.exists(fs_path):
        return image_url

    
    base, ext = os.path.splitext(fs_path)
    width = int(width)

    crop_pattern = f"{base}_crop_{width}x*{ext}"
    crop_matches = glob(crop_pattern)
    if crop_matches:
        return _fs_path_to_url(crop_matches[0])

    size_suffix = f"{width}xauto"
    variant_fs = f"{base}_{size_suffix}{ext}"

    if os.path.exists(variant_fs):
        return _fs_path_to_url(variant_fs)

    return image_url


@register.filter
def image_srcset(image_url, widths):
    """Return srcset attribute value for comma-separated widths string or list."""
    try:
        if not image_url:
            return ""

        if isinstance(widths, str):
            widths_list = [w.strip() for w in widths.split(",") if w.strip()]
        else:
            widths_list = list(widths)

        parts = []
        for w in widths_list:
            try:
                wi = int(w)
            except Exception:
                continue
            url = image_variant(image_url, wi)
            parts.append(f"{url} {wi}w")

        return ", ".join(parts)
    except Exception:
        return ""
