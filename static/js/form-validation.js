/**
 * Client-side form validation for FoodExpress
 * Mirrors server-side rules in core/validators.py
 */
document.addEventListener('DOMContentLoaded', function() {
    initFormValidation();
    initPhoneInputs();
    initCardNumberInput();
});

const RULES = {
    phone: {
        test: (v) => /^[6-9]\d{9}$/.test(v.replace(/\D/g, '')),
        message: 'Enter a valid 10-digit phone number starting with 6-9.',
    },
    email: {
        test: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim()),
        message: 'Enter a valid email address.',
    },
    username: {
        test: (v) => /^[a-zA-Z0-9_]{3,30}$/.test(v.trim()),
        message: 'Username must be 3-30 characters (letters, numbers, underscore).',
    },
    password: {
        test: (v) => v.length >= 8 && !/^\d+$/.test(v),
        message: 'Password must be at least 8 characters and not all numbers.',
    },
    name: {
        test: (v) => /^[a-zA-Z\s.'-]{2,50}$/.test(v.trim()),
        message: 'Name must be 2-50 letters only.',
    },
    address: {
        test: (v) => v.trim().length >= 10,
        message: 'Address must be at least 10 characters.',
    },
    cardNumber: {
        test: (v) => {
            const d = v.replace(/\D/g, '');
            return d.length === 16 && /^\d{16}$/.test(d);
        },
        message: 'Card number must be exactly 16 digits.',
    },
    cvv: {
        test: (v) => /^\d{3}$/.test(v.trim()),
        message: 'CVV must be exactly 3 digits.',
    },
    upi: {
        test: (v) => /^[a-z0-9._-]{2,256}@[a-z]{2,64}$/.test(v.trim().toLowerCase()),
        message: 'Enter a valid UPI ID (e.g. name@upi).',
    },
    walletPin: {
        test: (v) => v.trim() === '1234',
        message: 'Invalid wallet PIN. Demo PIN is 1234.',
    },
    rating: {
        test: (v) => v && parseInt(v) >= 1 && parseInt(v) <= 5,
        message: 'Please select a rating between 1 and 5 stars.',
    },
    review: {
        test: (v) => v.trim().length >= 10,
        message: 'Review must be at least 10 characters.',
    },
    price: {
        test: (v) => parseFloat(v) > 0,
        message: 'Price must be greater than zero.',
    },
    search: {
        test: (v) => !v.trim() || v.trim().length >= 2,
        message: 'Search must be at least 2 characters.',
    },
};

function showFieldError(input, message) {
    clearFieldError(input);
    input.classList.add('is-invalid');
    const err = document.createElement('div');
    err.className = 'form-error js-error';
    err.textContent = message;
    input.closest('.form-group')?.appendChild(err);
    if (!input.closest('.form-group')) {
        input.parentNode.insertBefore(err, input.nextSibling);
    }
}

function clearFieldError(input) {
    input.classList.remove('is-invalid');
    const group = input.closest('.form-group');
    if (group) {
        group.querySelectorAll('.js-error').forEach(el => el.remove());
    }
}

function validateField(input) {
    const name = input.name || '';
    const val = input.value || '';
    const type = input.type;
    const required = input.required || input.dataset.required === 'true';

    if (required && !val.trim()) {
        showFieldError(input, 'This field is required.');
        return false;
    }
    if (!val.trim() && !required) {
        clearFieldError(input);
        return true;
    }

    if (name.includes('phone') || input.dataset.validate === 'phone') {
        if (!RULES.phone.test(val)) { showFieldError(input, RULES.phone.message); return false; }
    }
    if (type === 'email' || name === 'email') {
        if (!RULES.email.test(val)) { showFieldError(input, RULES.email.message); return false; }
    }
    if (name === 'username') {
        if (!RULES.username.test(val)) { showFieldError(input, RULES.username.message); return false; }
    }
    if (name === 'password1') {
        if (!RULES.password.test(val)) { showFieldError(input, RULES.password.message); return false; }
    }
    if (name === 'password2') {
        const p1 = input.form?.querySelector('[name=password1]');
        if (p1 && val !== p1.value) { showFieldError(input, 'Passwords do not match.'); return false; }
    }
    if (name.includes('first_name') || name.includes('last_name') || name === 'card_holder') {
        if (val.trim() && !RULES.name.test(val)) { showFieldError(input, RULES.name.message); return false; }
    }
    if (name.includes('address') || name === 'delivery_address') {
        if (!RULES.address.test(val)) { showFieldError(input, RULES.address.message); return false; }
    }
    if (name === 'card_number') {
        if (!RULES.cardNumber.test(val)) { showFieldError(input, RULES.cardNumber.message); return false; }
    }
    if (name === 'cvv') {
        if (!RULES.cvv.test(val)) { showFieldError(input, RULES.cvv.message); return false; }
    }
    if (name === 'upi_id') {
        if (!RULES.upi.test(val)) { showFieldError(input, RULES.upi.message); return false; }
    }
    if (name === 'wallet_pin') {
        if (!RULES.walletPin.test(val)) { showFieldError(input, RULES.walletPin.message); return false; }
    }
    if (name === 'rating') {
        if (!RULES.rating.test(val)) { showFieldError(input, RULES.rating.message); return false; }
    }
    if (name === 'comment') {
        if (!RULES.review.test(val)) { showFieldError(input, RULES.review.message); return false; }
    }
    if (name === 'price' || name === 'discount_value') {
        if (!RULES.price.test(val)) { showFieldError(input, RULES.price.message); return false; }
    }
    if (name === 'q') {
        if (!RULES.search.test(val)) { showFieldError(input, RULES.search.message); return false; }
    }
    if (name === 'expiry_month') {
        const m = parseInt(val, 10);
        if (m < 1 || m > 12) { showFieldError(input, 'Month must be 01-12.'); return false; }
    }
    if (name === 'expiry_year') {
        const y = parseInt(val, 10);
        const fullY = y < 100 ? 2000 + y : y;
        if (fullY < new Date().getFullYear()) { showFieldError(input, 'Card has expired.'); return false; }
    }

    clearFieldError(input);
    return true;
}

function initFormValidation() {
    document.querySelectorAll('form[method="post"], form.search-bar, form.filter-bar').forEach(form => {
        form.classList.add('validated-form');
        form.querySelectorAll('input, textarea, select').forEach(input => {
            input.addEventListener('blur', () => validateField(input));
            input.addEventListener('input', () => {
                if (input.classList.contains('is-invalid')) validateField(input);
            });
        });
        form.addEventListener('submit', function(e) {
            let valid = true;
            form.querySelectorAll('input, textarea, select').forEach(input => {
                if (input.type === 'hidden' || input.disabled) return;
                const panel = input.closest('.payment-details-panel');
                if (panel && !panel.classList.contains('active')) return;
                if (input.offsetParent === null && !panel) return;
                if (!validateField(input)) valid = false;
            });
            const checkoutForm = document.getElementById('checkout-form');
            if (checkoutForm && form === checkoutForm && typeof validateClientSide === 'function') {
                if (!validateClientSide()) valid = false;
            }
            if (!valid) {
                e.preventDefault();
                const first = form.querySelector('.is-invalid');
                if (first) first.focus();
            }
        });
    });
}

function initPhoneInputs() {
    document.querySelectorAll('[name*="phone"], [data-validate="phone"]').forEach(input => {
        input.addEventListener('input', function() {
            this.value = this.value.replace(/\D/g, '').substring(0, 10);
        });
    });
}

function initCardNumberInput() {
    document.querySelectorAll('[name="card_number"]').forEach(input => {
        input.addEventListener('input', function() {
            let v = this.value.replace(/\D/g, '').substring(0, 16);
            this.value = v.replace(/(.{4})/g, '$1 ').trim();
        });
    });
    document.querySelectorAll('[name="cvv"]').forEach(input => {
        input.addEventListener('input', function() {
            this.value = this.value.replace(/\D/g, '').substring(0, 3);
        });
    });
    document.querySelectorAll('[name="wallet_pin"]').forEach(input => {
        input.addEventListener('input', function() {
            this.value = this.value.replace(/\D/g, '').substring(0, 4);
        });
    });
}
