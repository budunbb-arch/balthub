from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.template.loaders.filesystem import Loader as FilesystemLoader


def get_active_site_template():
    template = cache.get("site_template")
    if template is None:
        from apps.core.models import SiteSettings

        site_settings = SiteSettings.get_solo()
        template = site_settings.template if site_settings else "default"
        cache.set("site_template", template, 300)

    templates_dir = Path(settings.BASE_DIR) / "templates"
    template_dir = templates_dir / template
    if (
        template == "admin"
        or not template_dir.is_dir()
        or template_dir.parent.resolve() != templates_dir.resolve()
    ):
        return "default"

    return template


class ThemeTemplateLoader(FilesystemLoader):
    def get_template_sources(self, template_name):
        prefix = "default/"
        if not template_name.startswith(prefix):
            yield from super().get_template_sources(template_name)
            return

        template = get_active_site_template()
        relative_name = template_name[len(prefix):]
        yield from super().get_template_sources(f"{template}/{relative_name}")

        if template != "default":
            yield from super().get_template_sources(template_name)