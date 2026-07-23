import re
from datetime import date


# Demo/test cards that always pass validation
DUMMY_TEST_CARDS = {
    '4242424242424242': 'Visa (Test)',
    '4111111111111111': 'Visa (Test)',
    '5555555555554444': 'Mastercard (Test)',
    '378282246310005': 'Amex (Test)',
}


def normalize_card_number(number):
    return re.sub(r'\D', '', number or '')


def luhn_check(card_number):
    digits = normalize_card_number(card_number)
    if not digits or not digits.isdigit():
        return False
    total = 0
    reverse = digits[::-1]
    for i, d in enumerate(reverse):
        n = int(d)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def validate_card_number(card_number):
    digits = normalize_card_number(card_number)
    if len(digits) not in (15, 16):
        return False, 'Card number must be 15 or 16 digits.'
    if not luhn_check(digits):
        return False, 'Invalid card number. Please check and try again.'
    if digits not in DUMMY_TEST_CARDS:
        return False, (
            'Use a demo test card: 4242 4242 4242 4242, '
            '4111 1111 1111 1111, or 5555 5555 5555 4444'
        )
    return True, digits


def validate_expiry(month, year):
    try:
        m = int(month)
        y = int(year)
    except (TypeError, ValueError):
        return False, 'Invalid expiry date.'
    if m < 1 or m > 12:
        return False, 'Expiry month must be between 01 and 12.'
    if y < 100:
        y += 2000
    today = date.today()
    if y < today.year or (y == today.year and m < today.month):
        return False, 'Card has expired. Use a future expiry date.'
    return True, f'{m:02d}/{str(y)[-2:]}'


def validate_cvv(cvv, card_number=''):
    if not cvv or not re.match(r'^\d{3,4}$', str(cvv).strip()):
        return False, 'CVV must be 3 or 4 digits.'
    digits = normalize_card_number(card_number)
    if digits.startswith('3782') or len(digits) == 15:
        if len(str(cvv).strip()) != 4:
            return False, 'Amex cards require a 4-digit CVV.'
    return True, str(cvv).strip()


def validate_upi(upi_id):
    upi = (upi_id or '').strip().lower()
    if not re.match(r'^[a-z0-9._-]{2,256}@[a-z]{2,64}$', upi):
        return False, 'Enter a valid UPI ID (e.g. name@upi or 9876543210@paytm).'
    return True, upi


def mask_card_number(card_number):
    digits = normalize_card_number(card_number)
    if len(digits) >= 4:
        return f'**** **** **** {digits[-4:]}'
    return '****'
