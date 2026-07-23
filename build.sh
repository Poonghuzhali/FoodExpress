#!/usr/bin/env bash
set -o errexit

echo "==> Installing Python dependencies..."
pip install -r requirements.txt

echo "==> Collecting static files..."
python manage.py collectstatic --no-input

echo "==> Running database migrations..."
python manage.py migrate --no-input

echo "==> Seeding demo data..."
python manage.py seed_data

echo "==> Downloading images (optional)..."
python manage.py download_images || true

echo "==> Build finished successfully."
