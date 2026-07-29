# /opt/balthub/apps/modules/sitename.py

from apps.core.models import SiteSettings


MODULE = "default/modules/sitename.html"


def get_context(request, module):

    settings = SiteSettings.get_solo()

    return {
        "site_name": settings.site_name,
    }