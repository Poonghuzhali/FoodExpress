"""Shared field validators for all forms."""
import re
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email


PHONE_REGEX = re.compile(r'^[6-9]\d{9}$')
NAME_REGEX = re.compile(r"^[a-zA-Z\s.'-]{2,50}$")
USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_]{3,30}$')
UPI_REGEX = re.compile(r'^[a-z0-9._-]{2,256}@[a-z]{2,64}$')
VEHICLE_REGEX = re.compile(r'^[A-Z]{2}[0-9]{1,2}[A-Z]{0,3}[0-9]{4}$', re.I)
COUPON_CODE_REGEX = re.compile(r'^[A-Z0-9_-]{3,20}$', re.I)


def clean_phone(value, field_label='Phone number'):
    """Validate 10-digit Indian mobile number."""
    if not value:
        raise ValidationError(f'{field_label} is required.')
    digits = re.sub(r'\D', '', str(value).strip())
    if len(digits) != 10:
        raise ValidationError(f'{field_label} must be exactly 10 digits.')
    if not PHONE_REGEX.match(digits):
        raise ValidationError(f'{field_label} must start with 6, 7, 8, or 9.')
    return digits


def clean_optional_phone(value, field_label='Phone number'):
    if not value or not str(value).strip():
        return ''
    return clean_phone(value, field_label)


def clean_name(value, field_label='Name', min_len=2, max_len=50):
    value = (value or '').strip()
    if len(value) < min_len:
        raise ValidationError(f'{field_label} must be at least {min_len} characters.')
    if len(value) > max_len:
        raise ValidationError(f'{field_label} must be at most {max_len} characters.')
    if not NAME_REGEX.match(value):
        raise ValidationError(f'{field_label} may only contain letters, spaces, and hyphens.')
    return value


def clean_username(value):
    value = (value or '').strip()
    if len(value) < 3:
        raise ValidationError('Username must be at least 3 characters.')
    if len(value) > 30:
        raise ValidationError('Username must be at most 30 characters.')
    if not USERNAME_REGEX.match(value):
        raise ValidationError('Username may only contain letters, numbers, and underscores.')
    return value


def clean_email(value):
    value = (value or '').strip().lower()
    if not value:
        raise ValidationError('Email is required.')
    django_validate_email(value)
    return value


def clean_address(value, field_label='Address', min_len=10, required=True):
    value = (value or '').strip()
    if not value:
        if required:
            raise ValidationError(f'{field_label} is required.')
        return ''
    if len(value) < min_len:
        raise ValidationError(f'{field_label} must be at least {min_len} characters.')
    if len(value) > 500:
        raise ValidationError(f'{field_label} is too long (max 500 characters).')
    return value


def clean_password(value, field_label='Password'):
    value = value or ''
    if len(value) < 8:
        raise ValidationError(f'{field_label} must be at least 8 characters.')
    if len(value) > 128:
        raise ValidationError(f'{field_label} is too long.')
    if value.isdigit():
        raise ValidationError(f'{field_label} cannot be entirely numeric.')
    return value


def clean_card_number(value):
    digits = re.sub(r'\D', '', value or '')
    if len(digits) != 16:
        raise ValidationError('Card number must be exactly 16 digits.')
    if not digits.isdigit():
        raise ValidationError('Card number must contain digits only.')
    return digits


def clean_card_holder(value):
    value = (value or '').strip()
    if len(value) < 3:
        raise ValidationError('Cardholder name must be at least 3 characters.')
    if not re.match(r"^[a-zA-Z\s.'-]+$", value):
        raise ValidationError('Cardholder name must contain letters only.')
    return value


def clean_cvv(value):
    cvv = (value or '').strip()
    if not re.match(r'^\d{3}$', cvv):
        raise ValidationError('CVV must be exactly 3 digits.')
    return cvv


def clean_expiry_month(value):
    try:
        month = int(str(value).strip())
    except (TypeError, ValueError):
        raise ValidationError('Enter a valid expiry month (01–12).')
    if month < 1 or month > 12:
        raise ValidationError('Expiry month must be between 01 and 12.')
    return f'{month:02d}'


def clean_expiry_year(value):
    try:
        year = int(str(value).strip())
    except (TypeError, ValueError):
        raise ValidationError('Enter a valid expiry year.')
    if year < 100:
        year += 2000
    from datetime import date
    today = date.today()
    if year < today.year:
        raise ValidationError('Card has expired.')
    return str(year)


def clean_expiry_not_past(month, year):
    from datetime import date
    try:
        m = int(month)
        y = int(year)
        if y < 100:
            y += 2000
    except (TypeError, ValueError):
        raise ValidationError('Invalid expiry date.')
    today = date.today()
    if y < today.year or (y == today.year and m < today.month):
        raise ValidationError('Card expiry must be a future date.')


def clean_upi(value):
    upi = (value or '').strip().lower()
    if not UPI_REGEX.match(upi):
        raise ValidationError('Enter a valid UPI ID (e.g. name@upi).')
    return upi


def clean_wallet_pin(value):
    pin = (value or '').strip()
    if not re.match(r'^\d{4}$', pin):
        raise ValidationError('Wallet PIN must be exactly 4 digits.')
    return pin


def clean_price(value, field_label='Price'):
    if value is None or value == '':
        raise ValidationError(f'{field_label} is required.')
    try:
        price = Decimal(str(value))
    except Exception:
        raise ValidationError(f'{field_label} must be a valid number.')
    if price <= 0:
        raise ValidationError(f'{field_label} must be greater than zero.')
    if price > Decimal('99999'):
        raise ValidationError(f'{field_label} is too high.')
    return price


def clean_positive_int(value, field_label='Value', min_val=1, max_val=9999):
    try:
        num = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f'{field_label} must be a whole number.')
    if num < min_val or num > max_val:
        raise ValidationError(f'{field_label} must be between {min_val} and {max_val}.')
    return num


def clean_rating(value):
    try:
        rating = int(value)
    except (TypeError, ValueError):
        raise ValidationError('Please select a rating between 1 and 5 stars.')
    if rating < 1 or rating > 5:
        raise ValidationError('Rating must be between 1 and 5.')
    return rating


def clean_review_comment(value):
    value = (value or '').strip()
    if len(value) < 10:
        raise ValidationError('Review must be at least 10 characters.')
    if len(value) > 1000:
        raise ValidationError('Review must be at most 1000 characters.')
    return value


def clean_coupon_code(value):
    if not value:
        return ''
    code = value.strip().upper()
    if not COUPON_CODE_REGEX.match(code):
        raise ValidationError('Coupon code must be 3–20 letters, numbers, _ or -.')
    return code


def clean_search_query(value):
    value = (value or '').strip()
    if value and len(value) < 2:
        raise ValidationError('Search query must be at least 2 characters.')
    if len(value) > 100:
        raise ValidationError('Search query is too long.')
    return value


def clean_vehicle_number(value):
    value = (value or '').strip().upper()
    if not value:
        return ''
    if not VEHICLE_REGEX.match(value.replace(' ', '')):
        raise ValidationError('Enter a valid vehicle number (e.g. MH12AB1234).')
    return value.replace(' ', '')


def clean_restaurant_name(value):
    return clean_name(value, 'Restaurant name', min_len=3, max_len=200)


def clean_food_name(value):
    value = (value or '').strip()
    if len(value) < 2:
        raise ValidationError('Food name must be at least 2 characters.')
    if len(value) > 200:
        raise ValidationError('Food name is too long.')
    return value


def clean_category_name(value):
    value = (value or '').strip()
    if len(value) < 2:
        raise ValidationError('Category name must be at least 2 characters.')
    if len(value) > 100:
        raise ValidationError('Category name is too long.')
    return value
