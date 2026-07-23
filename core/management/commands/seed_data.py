from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from core.models import (
    User, FoodCategory, Restaurant, FoodItem, DeliveryPartner,
    Coupon, Cart
)
from core.image_utils import RESTAURANT_IMAGES, FOOD_IMAGES, CATEGORY_IMAGES


class Command(BaseCommand):
    help = 'Seed the database with sample data for FoodExpress'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        # Admin user
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin', email='admin@foodexpress.com',
                password='admin123', role='admin', first_name='Admin'
            )
            self.stdout.write(self.style.SUCCESS('Created admin (admin/admin123)'))

        # Categories
        categories_data = [
            ('Pizza', '🍕'), ('Burgers', '🍔'), ('Indian', '🍛'), ('Chinese', '🥡'),
            ('Desserts', '🍰'), ('Beverages', '🥤'), ('Healthy', '🥗'), ('Fast Food', '🍟'),
        ]
        categories = {}
        for name, icon in categories_data:
            cat, _ = FoodCategory.objects.get_or_create(name=name, defaults={'icon': icon})
            categories[name] = cat

        # Customer
        if not User.objects.filter(username='customer1').exists():
            customer = User.objects.create_user(
                username='customer1', email='customer@foodexpress.com',
                password='customer123', role='customer',
                first_name='John', last_name='Doe',
                phone='9876543210', address='123 Main Street, Mumbai'
            )
            Cart.objects.create(user=customer)
            self.stdout.write('Created customer (customer1/customer123)')

        # Delivery partner
        if not User.objects.filter(username='delivery1').exists():
            duser = User.objects.create_user(
                username='delivery1', email='delivery@foodexpress.com',
                password='delivery123', role='delivery',
                first_name='Mike', last_name='Rider', phone='9876543211'
            )
            DeliveryPartner.objects.create(user=duser, vehicle_type='Bike', vehicle_number='MH-01-AB-1234')
            self.stdout.write('Created delivery partner (delivery1/delivery123)')

        # Restaurants and menus
        restaurants_data = [
            {
                'username': 'pizzapalace', 'name': 'Pizza Palace', 'cuisine': 'Italian',
                'desc': 'Authentic wood-fired pizzas and Italian classics',
                'address': '45 Food Street, Bandra, Mumbai',
                'items': [
                    ('Margherita Pizza', 'Pizza', 299, True),
                    ('Pepperoni Feast', 'Pizza', 399, False),
                    ('Garlic Bread', 'Fast Food', 149, True),
                    ('Tiramisu', 'Desserts', 199, True),
                ],
            },
            {
                'username': 'burgerhub', 'name': 'Burger Hub', 'cuisine': 'American',
                'desc': 'Juicy gourmet burgers and crispy fries',
                'address': '78 Mall Road, Andheri, Mumbai',
                'items': [
                    ('Classic Cheeseburger', 'Burgers', 249, False),
                    ('Veggie Deluxe', 'Burgers', 199, True),
                    ('Loaded Fries', 'Fast Food', 149, True),
                    ('Chocolate Shake', 'Beverages', 129, True),
                ],
            },
            {
                'username': 'spicegarden', 'name': 'Spice Garden', 'cuisine': 'Indian',
                'desc': 'Traditional Indian cuisine with a modern twist',
                'address': '12 Heritage Lane, Colaba, Mumbai',
                'items': [
                    ('Butter Chicken', 'Indian', 349, False),
                    ('Paneer Tikka', 'Indian', 279, True),
                    ('Biryani Special', 'Indian', 329, False),
                    ('Garlic Naan', 'Indian', 49, True),
                ],
            },
            {
                'username': 'dragonwok', 'name': 'Dragon Wok', 'cuisine': 'Chinese',
                'desc': 'Fresh wok-tossed noodles and dim sum',
                'address': '33 China Town, Powai, Mumbai',
                'items': [
                    ('Hakka Noodles', 'Chinese', 219, True),
                    ('Kung Pao Chicken', 'Chinese', 299, False),
                    ('Spring Rolls', 'Chinese', 149, True),
                    ('Hot & Sour Soup', 'Chinese', 129, True),
                ],
            },
            {
                'username': 'greenbowl', 'name': 'Green Bowl', 'cuisine': 'Healthy',
                'desc': 'Fresh salads, bowls, and smoothies',
                'address': '56 Wellness Ave, Juhu, Mumbai',
                'items': [
                    ('Caesar Salad', 'Healthy', 249, True),
                    ('Quinoa Bowl', 'Healthy', 299, True),
                    ('Green Smoothie', 'Beverages', 149, True),
                    ('Avocado Toast', 'Healthy', 199, True),
                ],
            },
        ]

        for rdata in restaurants_data:
            if User.objects.filter(username=rdata['username']).exists():
                continue
            user = User.objects.create_user(
                username=rdata['username'],
                email=f"{rdata['username']}@foodexpress.com",
                password='restaurant123',
                role='restaurant',
                first_name=rdata['name'],
                phone='9876543200',
            )
            restaurant = Restaurant.objects.create(
                user=user,
                name=rdata['name'],
                description=rdata['desc'],
                address=rdata['address'],
                phone='9876543200',
                email=f"{rdata['username']}@foodexpress.com",
                cuisine_type=rdata['cuisine'],
                rating=Decimal('4.5'),
                delivery_time='25-35 min',
                min_order=Decimal('99'),
            )
            for item_name, cat_name, price, is_veg in rdata['items']:
                FoodItem.objects.create(
                    restaurant=restaurant,
                    category=categories.get(cat_name),
                    name=item_name,
                    description=f'Delicious {item_name} from {rdata["name"]}',
                    price=Decimal(str(price)),
                    is_vegetarian=is_veg,
                    is_available=True,
                )
            self.stdout.write(f'Created restaurant: {rdata["name"]} ({rdata["username"]}/restaurant123)')

        # Coupons
        Coupon.objects.get_or_create(
            code='WELCOME20',
            defaults={
                'description': '20% off on first order',
                'discount_type': 'percent',
                'discount_value': Decimal('20'),
                'min_order_amount': Decimal('199'),
                'max_discount': Decimal('150'),
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=365),
                'usage_limit': 1000,
                'is_active': True,
            }
        )
        Coupon.objects.get_or_create(
            code='FLAT50',
            defaults={
                'description': 'Flat ₹50 off',
                'discount_type': 'fixed',
                'discount_value': Decimal('50'),
                'min_order_amount': Decimal('299'),
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=90),
                'usage_limit': 500,
                'is_active': True,
            }
        )

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
        self._clear_external_image_urls()
        self.stdout.write('')
        self.stdout.write('Demo Accounts:')
        self.stdout.write('  Admin:     admin / admin123')
        self.stdout.write('  Customer:  customer1 / customer123')
        self.stdout.write('  Delivery:  delivery1 / delivery123')
        self.stdout.write('  Restaurant: pizzapalace / restaurant123')

    def _clear_external_image_urls(self):
        """Remove broken external URLs so local static images are used."""
        from django.conf import settings

        def is_local(url):
            return url and url.startswith(settings.STATIC_URL)

        for r in Restaurant.objects.all():
            if not is_local(r.cover_image_url):
                r.cover_image_url = RESTAURANT_IMAGES.get(r.name, '')
                r.save(update_fields=['cover_image_url'])

        for item in FoodItem.objects.all():
            if not is_local(item.image_url):
                item.image_url = FOOD_IMAGES.get(item.name, '')
                item.save(update_fields=['image_url'])

        for cat in FoodCategory.objects.all():
            if not is_local(cat.image_url):
                cat.image_url = CATEGORY_IMAGES.get(cat.name, '')
                cat.save(update_fields=['image_url'])

        self.stdout.write('Updated image paths to local static files.')
