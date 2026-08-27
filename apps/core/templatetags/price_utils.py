from django import template

register = template.Library()


@register.filter
def format_price(value):
    try:
        number = int(value)
        return f"{number:,}".replace(",", " ")
    except (TypeError, ValueError):
        return value
