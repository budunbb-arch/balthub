from django import template

register = template.Library()

@register.filter
def get_item(querydict, key):
    return querydict.get(key)


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):

    query = context["request"].GET.copy()

    for key, value in kwargs.items():

        query.pop(key, None)

        if value is not None:
            query[key] = value

    return query.urlencode()