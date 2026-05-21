from django import template

register = template.Library()

@register.filter
def get_item(querydict, key):
    return querydict.get(key)