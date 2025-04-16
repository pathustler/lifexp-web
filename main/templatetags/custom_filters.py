from django import template
register = template.Library()
from main.models import Post
import roman

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

@register.filter
def roman(value):
    try:
        return roman.toRoman(int(value))
    except Exception:
        return value  # fallback if something fails
    
@register.filter
def dict_get(d, key):
    return d.get(key)

