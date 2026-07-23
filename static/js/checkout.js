document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('checkout-form');
    if (!form) return;

    const panels = {
        card: document.getElementById('payment-card'),
        upi: document.getElementById('payment-upi'),
        wallet: document.getElementById('payment-wallet'),
        cod: document.getElementById('payment-cod'),
    };
    const payBtn = document.getElementById('pay-btn');
    const errorBox = document.getElementById('payment-errors');

    const TEST_CARDS = ['4242424242424242', '4111111111111111', '5555555555554444'];

    function getSelectedMethod() {
        const checked = form.querySelector('input[name="payment_method"]:checked');
        return checked ? checked.value : 'card';
    }

    function showPanel(method) {
        Object.entries(panels).forEach(([key, panel]) => {
            if (panel) panel.classList.toggle('active', key === method);
        });
        document.querySelectorAll('.payment-option').forEach(opt => {
            opt.classList.toggle('selected', opt.dataset.method === method);
        });
        if (payBtn) {
            payBtn.textContent = method === 'cod' ? '📦 Place Order (COD)' : '🔒 Validate & Place Order';
        }
    }

    form.querySelectorAll('input[name="payment_method"]').forEach(radio => {
        radio.addEventListener('change', () => showPanel(getSelectedMethod()));
    });
    showPanel(getSelectedMethod());

    function luhnCheck(num) {
        const digits = num.replace(/\D/g, '');
        let sum = 0;
        for (let i = 0; i < digits.length; i++) {
            let n = parseInt(digits[digits.length - 1 - i], 10);
            if (i % 2 === 1) { n *= 2; if (n > 9) n -= 9; }
            sum += n;
        }
        return sum % 10 === 0;
    }

    function showError(msg) {
        if (!errorBox) return;
        errorBox.textContent = msg;
        errorBox.style.display = 'block';
        errorBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function hideError() {
        if (errorBox) errorBox.style.display = 'none';
    }

    window.validateClientSide = function validateClientSide() {
        hideError();
        const method = getSelectedMethod();

        if (method === 'card') {
            const holder = form.querySelector('[name="card_holder"]').value.trim();
            const number = form.querySelector('[name="card_number"]').value.replace(/\D/g, '');
            const month = form.querySelector('[name="expiry_month"]').value.trim();
            const year = form.querySelector('[name="expiry_year"]').value.trim();
            const cvv = form.querySelector('[name="cvv"]').value.trim();

            if (holder.length < 3) return showError('Enter the cardholder name (letters only).'), false;
            if (!/^[a-zA-Z\s.'-]+$/.test(holder)) return showError('Cardholder name must contain letters only.'), false;
            if (number.length !== 16) return showError('Card number must be exactly 16 digits.'), false;
            if (!luhnCheck(number)) return showError('Invalid card number.'), false;
            if (!TEST_CARDS.includes(number)) return showError('Use demo card: 4242 4242 4242 4242'), false;

            const m = parseInt(month, 10);
            let y = parseInt(year, 10);
            if (y < 100) y += 2000;
            const now = new Date();
            if (m < 1 || m > 12 || y < now.getFullYear() || (y === now.getFullYear() && m < now.getMonth() + 1)) {
                return showError('Card expiry must be a future date.'), false;
            }
            if (!/^\d{3}$/.test(cvv)) return showError('CVV must be exactly 3 digits.'), false;
        }

        if (method === 'upi') {
            const upi = form.querySelector('[name="upi_id"]').value.trim().toLowerCase();
            if (!/^[a-z0-9._-]{2,256}@[a-z]{2,64}$/.test(upi)) {
                return showError('Enter a valid UPI ID (e.g. name@upi).'), false;
            }
        }

        if (method === 'wallet') {
            const pin = form.querySelector('[name="wallet_pin"]').value.trim();
            if (!/^\d{4}$/.test(pin)) return showError('Wallet PIN must be exactly 4 digits.'), false;
            if (pin !== '1234') return showError('Invalid wallet PIN. Demo PIN is 1234.'), false;
        }

        return true;
    };

    form.addEventListener('submit', function(e) {
        if (!window.validateClientSide()) {
            e.preventDefault();
            return;
        }
        if (payBtn) {
            payBtn.disabled = true;
            payBtn.textContent = 'Processing payment...';
        }
    });
});
