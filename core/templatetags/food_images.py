from django import template
from core.image_utils import (
    get_restaurant_image, get_food_image, get_category_image, HERO_IMAGE,
)

register = template.Library()


@register.simple_tag
def restaurant_image(restaurant, cover=False):
    return get_restaurant_image(restaurant, cover=cover)


@register.simple_tag
def food_image(food_item, thumb=False):
    return get_food_image(food_item, thumb=thumb)


@register.simple_tag
def category_image(category):
    return get_category_image(category)


@register.simple_tag
def hero_image():
    return HERO_IMAGE
