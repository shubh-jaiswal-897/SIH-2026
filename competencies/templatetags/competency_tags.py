from django import template

register = template.Library()

@register.simple_tag
def count_gaps(gaps):
    if not gaps:
        return 0
    return sum(1 for g in gaps if g.get('gap', 0) > 0)

@register.filter
def get_item(dictionary, key):
    if not dictionary:
        return None
    return dictionary.get(str(key)) or dictionary.get(key)

