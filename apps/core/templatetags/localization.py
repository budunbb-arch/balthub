# /opt/balthub/apps/core/templatetags/localization.py

from django import template

from apps.core.localization import t

register = template.Library()


@register.simple_tag
def tr(key):

    return t(key)


@register.filter
def yesno_i18n(value):

    from apps.core.localization import t

    return t("common.yes") if value else t("common.no")