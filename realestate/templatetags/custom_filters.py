from django import template
from django import template
from realestate.models import Seller  # Adjust if in another app

register = template.Library()

@register.filter
def has_seller(user):
    return hasattr(user, 'seller')

register = template.Library()

@register.filter
def class_name(value):
    return value.__class__.__name__
