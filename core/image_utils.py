"""Local static image paths for restaurants, dishes, and categories."""

from django.conf import settings


def _static(path):
    return f"{settings.STATIC_URL}images/{path}"


HERO_IMAGE = _static('hero.jpg')
DEFAULT_RESTAURANT = _static('default-restaurant.jpg')
DEFAULT_FOOD = _static('default-food.jpg')

RESTAURANT_IMAGES = {
    'Pizza Palace': _static('restaurants/pizza-palace.jpg'),
    'Burger Hub': _static('restaurants/burger-hub.jpg'),
    'Spice Garden': _static('restaurants/spice-garden.jpg'),
    'Dragon Wok': _static('restaurants/dragon-wok.jpg'),
    'Green Bowl': _static('restaurants/green-bowl.jpg'),
}

RESTAURANT_COVER_IMAGES = {
    'Pizza Palace': _static('restaurants/pizza-palace-cover.jpg'),
    'Burger Hub': _static('restaurants/burger-hub-cover.jpg'),
    'Spice Garden': _static('restaurants/spice-garden-cover.jpg'),
    'Dragon Wok': _static('restaurants/dragon-wok-cover.jpg'),
    'Green Bowl': _static('restaurants/green-bowl-cover.jpg'),
}

FOOD_IMAGES = {
    'Margherita Pizza': _static('food/margherita-pizza.jpg'),
    'Pepperoni Feast': _static('food/pepperoni-feast.jpg'),
    'Garlic Bread': _static('food/garlic-bread.jpg'),
    'Tiramisu': _static('food/tiramisu.jpg'),
    'Classic Cheeseburger': _static('food/classic-cheeseburger.jpg'),
    'Veggie Deluxe': _static('food/veggie-deluxe.jpg'),
    'Loaded Fries': _static('food/loaded-fries.jpg'),
    'Chocolate Shake': _static('food/chocolate-shake.jpg'),
    'Butter Chicken': _static('food/butter-chicken.jpg'),
    'Paneer Tikka': _static('food/paneer-tikka.jpg'),
    'Biryani Special': _static('food/biryani-special.jpg'),
    'Garlic Naan': _static('food/garlic-naan.jpg'),
    'Hakka Noodles': _static('food/hakka-noodles.jpg'),
    'Kung Pao Chicken': _static('food/kung-pao-chicken.jpg'),
    'Spring Rolls': _static('food/spring-rolls.jpg'),
    'Hot & Sour Soup': _static('food/hot-sour-soup.jpg'),
    'Caesar Salad': _static('food/caesar-salad.jpg'),
    'Quinoa Bowl': _static('food/quinoa-bowl.jpg'),
    'Green Smoothie': _static('food/green-smoothie.jpg'),
    'Avocado Toast': _static('food/avocado-toast.jpg'),
}

FOOD_THUMB_IMAGES = FOOD_IMAGES.copy()

CATEGORY_IMAGES = {
    'Pizza': _static('categories/pizza.jpg'),
    'Burgers': _static('categories/burgers.jpg'),
    'Indian': _static('categories/indian.jpg'),
    'Chinese': _static('categories/chinese.jpg'),
    'Desserts': _static('categories/desserts.jpg'),
    'Beverages': _static('categories/beverages.jpg'),
    'Healthy': _static('categories/healthy.jpg'),
    'Fast Food': _static('categories/fast-food.jpg'),
}

CUISINE_FALLBACK = {
    'Italian': RESTAURANT_IMAGES['Pizza Palace'],
    'American': RESTAURANT_IMAGES['Burger Hub'],
    'Indian': RESTAURANT_IMAGES['Spice Garden'],
    'Chinese': RESTAURANT_IMAGES['Dragon Wok'],
    'Healthy': RESTAURANT_IMAGES['Green Bowl'],
}


def _is_local_url(url):
    return url and url.startswith(settings.STATIC_URL)


def get_restaurant_image(restaurant, cover=False):
    if cover:
        if _is_local_url(getattr(restaurant, 'cover_image_url', '')):
            return restaurant.cover_image_url
        if restaurant.cover_image:
            return restaurant.cover_image.url
        return RESTAURANT_COVER_IMAGES.get(
            restaurant.name,
            CUISINE_FALLBACK.get(restaurant.cuisine_type, DEFAULT_RESTAURANT),
        )

    if _is_local_url(getattr(restaurant, 'cover_image_url', '')):
        return restaurant.cover_image_url
    if restaurant.cover_image:
        return restaurant.cover_image.url
    if restaurant.logo:
        return restaurant.logo.url
    return RESTAURANT_IMAGES.get(
        restaurant.name,
        CUISINE_FALLBACK.get(restaurant.cuisine_type, DEFAULT_RESTAURANT),
    )


def get_food_image(food_item, thumb=False):
    if _is_local_url(getattr(food_item, 'image_url', '')):
        return food_item.image_url
    if food_item.image:
        return food_item.image.url
    if food_item.name in FOOD_IMAGES:
        return FOOD_IMAGES[food_item.name]
    if food_item.category and food_item.category.name in CATEGORY_IMAGES:
        return CATEGORY_IMAGES[food_item.category.name]
    return DEFAULT_FOOD


def get_category_image(category):
    if _is_local_url(getattr(category, 'image_url', '')):
        return category.image_url
    if category.image:
        return category.image.url
    return CATEGORY_IMAGES.get(category.name, DEFAULT_FOOD)
