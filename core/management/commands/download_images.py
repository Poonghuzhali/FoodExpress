"""Download food images to static/images/ for reliable local serving."""
import urllib.request
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

# Real food photos from Unsplash (verified via GET download)
UNSPLASH = 'https://images.unsplash.com/{id}?auto=format&fit=crop&w={w}&h={h}&q=80'


def u(photo_id, w=400, h=180):
    return UNSPLASH.format(id=photo_id, w=w, h=h)


IMAGE_SOURCES = {
    'hero.jpg': u('photo-1504674900247-0877df9cc836', 600, 420),
    'default-restaurant.jpg': u('photo-1517248135467-4c7edcad34c4', 400, 180),
    'default-food.jpg': u('photo-1546069901-ba9599a7e63c', 400, 180),
    # Restaurants
    'restaurants/pizza-palace.jpg': u('photo-1574071318508-1cdbab80d002', 400, 180),
    'restaurants/burger-hub.jpg': u('photo-1552566626-52f8b828add9', 400, 180),
    'restaurants/spice-garden.jpg': u('photo-1563379091339-03b21ab4a4f8', 400, 180),
    'restaurants/dragon-wok.jpg': u('photo-1555396273-367ea4eb4db5', 400, 180),
    'restaurants/green-bowl.jpg': u('photo-1512621776951-a57141f2eefd', 400, 180),
    'restaurants/pizza-palace-cover.jpg': u('photo-1517248135467-4c7edcad34c4', 1200, 220),
    'restaurants/burger-hub-cover.jpg': u('photo-1552566626-52f8b828add9', 1200, 220),
    'restaurants/spice-garden-cover.jpg': u('photo-1631452180519-c014fe946bc7', 1200, 220),
    'restaurants/dragon-wok-cover.jpg': u('photo-1555396273-367ea4eb4db5', 1200, 220),
    'restaurants/green-bowl-cover.jpg': u('photo-1546069901-ba9599a7e63c', 1200, 220),
    # Food items
    'food/margherita-pizza.jpg': u('photo-1574071318508-1cdbab80d002', 400, 180),
    'food/pepperoni-feast.jpg': u('photo-1628840042765-356cda07504e', 400, 180),
    'food/garlic-bread.jpg': u('photo-1509440159596-0249088772ff', 400, 180),
    'food/tiramisu.jpg': u('photo-1571877227200-a0d98ea607e9', 400, 180),
    'food/classic-cheeseburger.jpg': u('photo-1550547660-d9450f859349', 400, 180),
    'food/veggie-deluxe.jpg': u('photo-1586190848861-99aa4a171e90', 400, 180),
    'food/loaded-fries.jpg': u('photo-1565299624946-b28f40a0ae38', 400, 180),
    'food/chocolate-shake.jpg': u('photo-1488477181946-6428a0291777', 400, 180),
    'food/butter-chicken.jpg': u('photo-1631452180519-c014fe946bc7', 400, 180),
    'food/paneer-tikka.jpg': u('photo-1565557623262-b51c2513a641', 400, 180),
    'food/biryani-special.jpg': u('photo-1563379091339-03b21ab4a4f8', 400, 180),
    'food/garlic-naan.jpg': u('photo-1509440159596-0249088772ff', 400, 180),
    'food/hakka-noodles.jpg': u('photo-1555396273-367ea4eb4db5', 400, 180),
    'food/kung-pao-chicken.jpg': u('photo-1467003909585-2f8a72700288', 400, 180),
    'food/spring-rolls.jpg': u('photo-1555396273-367ea4eb4db5', 400, 180),
    'food/hot-sour-soup.jpg': u('photo-1547592166-23ac45744acd', 400, 180),
    'food/caesar-salad.jpg': u('photo-1512621776951-a57141f2eefd', 400, 180),
    'food/quinoa-bowl.jpg': u('photo-1546069901-ba9599a7e63c', 400, 180),
    'food/green-smoothie.jpg': u('photo-1512621776951-a57141f2eefd', 400, 180),
    'food/avocado-toast.jpg': u('photo-1546069901-ba9599a7e63c', 400, 180),
    # Categories
    'categories/pizza.jpg': u('photo-1574071318508-1cdbab80d002', 200, 200),
    'categories/burgers.jpg': u('photo-1550547660-d9450f859349', 200, 200),
    'categories/indian.jpg': u('photo-1563379091339-03b21ab4a4f8', 200, 200),
    'categories/chinese.jpg': u('photo-1555396273-367ea4eb4db5', 200, 200),
    'categories/desserts.jpg': u('photo-1488477181946-6428a0291777', 200, 200),
    'categories/beverages.jpg': u('photo-1488477181946-6428a0291777', 200, 200),
    'categories/healthy.jpg': u('photo-1512621776951-a57141f2eefd', 200, 200),
    'categories/fast-food.jpg': u('photo-1565299624946-b28f40a0ae38', 200, 200),
    # Promo banner
    'promo/pizza.jpg': u('photo-1574071318508-1cdbab80d002', 200, 200),
    'promo/burger.jpg': u('photo-1550547660-d9450f859349', 200, 200),
    'promo/biryani.jpg': u('photo-1563379091339-03b21ab4a4f8', 200, 200),
}


class Command(BaseCommand):
    help = 'Download images to static/images/ for offline reliable loading'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Re-download even if file exists')

    def handle(self, *args, **options):
        base = Path(settings.STATICFILES_DIRS[0]) / 'images'
        base.mkdir(parents=True, exist_ok=True)
        ok, fail = 0, 0
        force = options['force']

        for rel_path, url in IMAGE_SOURCES.items():
            dest = base / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists() and dest.stat().st_size > 1000 and not force:
                ok += 1
                continue
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = resp.read()
                if len(data) < 500:
                    raise ValueError('Downloaded file too small')
                dest.write_bytes(data)
                self.stdout.write(self.style.SUCCESS(f'  OK: {rel_path} ({len(data):,} bytes)'))
                ok += 1
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f'  FAIL: {rel_path} — {exc}'))
                fail += 1

        self.stdout.write(self.style.SUCCESS(f'\nDownloaded {ok} images, {fail} failed.'))
