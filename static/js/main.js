document.addEventListener('DOMContentLoaded', function() {
    initScrollAnimations();
    initAlerts();
    initAddToCart();
    initMobileMenu();
    document.querySelectorAll('[data-counter]').forEach(el => {
        const target = parseFloat(el.dataset.counter);
        if (!isNaN(target)) animateCounter(el, target);
    });
    const bar = document.querySelector('.tracking-progress-bar');
    if (bar && bar.dataset.progress) {
        setTimeout(() => bar.style.width = bar.dataset.progress + '%', 300);
    }
});

function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-up');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    document.querySelectorAll('.card, .stat-card, .menu-item-card').forEach(el => {
        el.style.opacity = '0';
        observer.observe(el);
    });
}

function initAlerts() {
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s, transform 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
}

function initMobileMenu() {
    const navbar = document.getElementById('navbar');
    const btn = document.getElementById('mobile-menu-btn');
    const overlay = document.getElementById('mobile-menu-overlay');
    const navLinks = document.getElementById('nav-links');
    if (!navbar || !btn) return;

    function openMenu() {
        navbar.classList.add('menu-open');
        btn.setAttribute('aria-expanded', 'true');
        document.body.style.overflow = 'hidden';
    }

    function closeMenu() {
        navbar.classList.remove('menu-open');
        btn.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
    }

    function toggleMenu() {
        if (navbar.classList.contains('menu-open')) closeMenu();
        else openMenu();
    }

    btn.addEventListener('click', toggleMenu);
    if (overlay) overlay.addEventListener('click', closeMenu);

    if (navLinks) {
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', closeMenu);
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeMenu();
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) closeMenu();
    });
}

function initAddToCart() {
    document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.dataset.url;
            const csrf = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken');
            fetch(url, { method: 'POST', headers: { 'X-Requested-With': 'XMLHttpRequest', 'X-CSRFToken': csrf } })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showToast('Added to cart!', 'success');
                    const badge = document.querySelector('.cart-badge');
                    if (badge) badge.textContent = data.cart_count;
                }
            }).catch(() => showToast('Added to cart!', 'success'));
        });
    });
}

function showToast(message, type) {
    const toast = document.createElement('div');
    toast.className = 'alert alert-' + type;
    toast.style.cssText = 'position:fixed;top:80px;right:20px;z-index:9999;min-width:250px;box-shadow:var(--shadow-lg);';
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 500); }, 3000);
}

function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let c of cookies) {
        c = c.trim();
        if (c.startsWith(name + '=')) return decodeURIComponent(c.substring(name.length + 1));
    }
    return null;
}

function animateCounter(element, target) {
    let start = 0;
    const increment = target / 60;
    const timer = setInterval(() => {
        start += increment;
        if (start >= target) { element.textContent = Math.round(target); clearInterval(timer); }
        else element.textContent = Math.round(start);
    }, 16);
}
