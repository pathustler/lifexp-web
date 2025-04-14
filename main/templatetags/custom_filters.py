from django import template
register = template.Library()
from main.models import Post

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def split(value, delimiter):
    return value.split(delimiter)


@register.filter
def lookup_post(post_id):
    try:
        return Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return None
