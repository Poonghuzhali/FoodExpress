from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse
from functools import wraps

from .models import (
    User, Restaurant, FoodCategory, FoodItem, Cart, CartItem,
    Order, OrderItem, Payment, DeliveryPartner, Review, Coupon
)
from .forms import (
    CustomerRegistrationForm, RestaurantRegistrationForm, DeliveryRegistrationForm,
    LoginForm, RestaurantProfileForm, FoodItemForm, ReviewForm,
    CheckoutForm, UserProfileForm, CouponForm, SearchForm
)
from .utils import send_order_notification, send_order_confirmation_email, get_order_status_message


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in roles and not request.user.is_superuser:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ==================== PUBLIC VIEWS ====================

def home(request):
    restaurants = Restaurant.objects.filter(is_approved=True, is_open=True)[:8]
    categories = FoodCategory.objects.filter(is_active=True)[:8]
    featured_items = FoodItem.objects.filter(is_available=True).select_related('restaurant')[:6]
    return render(request, 'home.html', {
        'restaurants': restaurants,
        'categories': categories,
        'featured_items': featured_items,
    })


def restaurant_list(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    cuisine = request.GET.get('cuisine', '')

    restaurants = Restaurant.objects.filter(is_approved=True)
    if query:
        restaurants = restaurants.filter(
            Q(name__icontains=query) | Q(cuisine_type__icontains=query) | Q(description__icontains=query)
        )
    if category_id:
        restaurants = restaurants.filter(menu_items__category_id=category_id).distinct()
    if cuisine:
        restaurants = restaurants.filter(cuisine_type__icontains=cuisine)

    categories = FoodCategory.objects.filter(is_active=True)
    cuisines = Restaurant.objects.filter(is_approved=True).values_list('cuisine_type', flat=True).distinct()

    return render(request, 'customer/restaurant_list.html', {
        'restaurants': restaurants,
        'categories': categories,
        'cuisines': [c for c in cuisines if c],
        'query': query,
        'selected_category': category_id,
        'selected_cuisine': cuisine,
    })


def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk, is_approved=True)
    menu_items = restaurant.menu_items.filter(is_available=True).select_related('category')
    categories = FoodCategory.objects.filter(items__restaurant=restaurant).distinct()
    reviews = restaurant.reviews.select_related('customer').all()[:10]
    review_stats = restaurant.reviews.aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id'),
    )
    return render(request, 'customer/restaurant_detail.html', {
        'restaurant': restaurant,
        'menu_items': menu_items,
        'categories': categories,
        'reviews': reviews,
        'review_stats': review_stats,
    })


def search(request):
    form = SearchForm(request.GET)
    query = ''
    restaurants = Restaurant.objects.filter(is_approved=True)
    food_items = FoodItem.objects.filter(is_available=True)

    if form.is_valid():
        query = form.cleaned_data.get('q', '')
    elif request.GET.get('q'):
        messages.warning(request, 'Search query must be at least 2 characters.')
        return render(request, 'customer/search.html', {
            'query': request.GET.get('q', ''),
            'restaurants': [],
            'food_items': [],
            'form': form,
        })

    if query:
        restaurants = restaurants.filter(
            Q(name__icontains=query) | Q(cuisine_type__icontains=query)
        )
        food_items = food_items.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    return render(request, 'customer/search.html', {
        'query': query,
        'restaurants': restaurants[:10],
        'food_items': food_items.select_related('restaurant')[:10],
        'form': form,
    })


# ==================== AUTH VIEWS ====================

def register_customer(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Cart.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Welcome to FoodExpress! Your account has been created.')
            return redirect('home')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'auth/register_customer.html', {'form': form})


def register_restaurant(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RestaurantRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Restaurant registered successfully!')
            return redirect('restaurant_dashboard')
    else:
        form = RestaurantRegistrationForm()
    return render(request, 'auth/register_restaurant.html', {'form': form})


def register_delivery(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = DeliveryRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Delivery partner account created!')
            return redirect('delivery_dashboard')
    else:
        form = DeliveryRegistrationForm()
    return render(request, 'auth/register_delivery.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect_dashboard(request.user)
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect_dashboard(user)
        messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})


def redirect_dashboard(user):
    if user.is_superuser or user.role == 'admin':
        return redirect('admin_dashboard')
    elif user.role == 'restaurant':
        return redirect('restaurant_dashboard')
    elif user.role == 'delivery':
        return redirect('delivery_dashboard')
    return redirect('home')


def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ==================== CUSTOMER VIEWS ====================

@login_required
@role_required('customer')
def customer_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('customer_profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'customer/profile.html', {'form': form})


@login_required
@role_required('customer')
def add_to_cart(request, item_id):
    food_item = get_object_or_404(FoodItem, pk=item_id, is_available=True)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    if cart.restaurant and cart.restaurant != food_item.restaurant:
        messages.warning(request, 'Please clear your cart before ordering from a different restaurant.')
        return redirect('restaurant_detail', pk=food_item.restaurant.pk)

    cart.restaurant = food_item.restaurant
    cart.save()

    cart_item, created = CartItem.objects.get_or_create(cart=cart, food_item=food_item)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': cart.item_count})
    messages.success(request, f'{food_item.name} added to cart!')
    return redirect('restaurant_detail', pk=food_item.restaurant.pk)


@login_required
@role_required('customer')
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'customer/cart.html', {'cart': cart})


@login_required
@role_required('customer')
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    action = request.POST.get('action')
    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    elif action == 'remove':
        cart_item.delete()
    return redirect('view_cart')


@login_required
@role_required('customer')
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('restaurant_list')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            subtotal = cart.total
            discount = Decimal('0')
            coupon = None
            coupon_code = form.cleaned_data.get('coupon_code', '').strip().upper()
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code__iexact=coupon_code)
                    discount = Decimal(str(coupon.calculate_discount(subtotal)))
                except Coupon.DoesNotExist:
                    messages.warning(request, 'Invalid coupon code.')

            delivery_fee = Decimal(str(settings.DELIVERY_FEE))
            tax = (subtotal - discount) * Decimal(str(settings.TAX_RATE))
            total = subtotal - discount + delivery_fee + tax

            order = Order.objects.create(
                customer=request.user,
                restaurant=cart.restaurant,
                coupon=coupon,
                delivery_address=form.cleaned_data['delivery_address'],
                delivery_phone=form.cleaned_data['delivery_phone'],
                special_instructions=form.cleaned_data.get('special_instructions', ''),
                subtotal=subtotal,
                discount=discount,
                delivery_fee=delivery_fee,
                tax=tax.quantize(Decimal('0.01')),
                total=total.quantize(Decimal('0.01')),
            )

            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    food_item=item.food_item,
                    food_name=item.food_item.name,
                    price=item.food_item.price,
                    quantity=item.quantity,
                )

            payment_method = form.cleaned_data['payment_method']
            payment_status = 'completed' if payment_method != 'cod' else 'pending'
            payment = Payment.objects.create(
                order=order,
                payment_method=payment_method,
                amount=total,
                status=payment_status,
            )
            if payment_method == 'card':
                payment._card_number = form.cleaned_data.get('card_number', '')

            if coupon:
                coupon.used_count += 1
                coupon.save()

            cart.items.all().delete()
            cart.restaurant = None
            cart.save()

            email_sent = send_order_confirmation_email(order, payment)
            send_order_notification(
                order,
                f'Order Received - #{order.order_id}',
                get_order_status_message(order),
            )
            if email_sent:
                messages.success(
                    request,
                    f'Order placed! Confirmation email sent to {request.user.email}. Order ID: {order.order_id}'
                )
            else:
                messages.success(request, f'Order placed successfully! Order ID: {order.order_id}')
            return redirect('order_detail', order_id=order.order_id)
    else:
        form = CheckoutForm(initial={
            'delivery_address': request.user.address,
            'delivery_phone': request.user.phone,
        })

    return render(request, 'customer/checkout.html', {'cart': cart, 'form': form})


@login_required
@role_required('customer')
def order_list(request):
    orders = request.user.orders.select_related('restaurant').all()
    return render(request, 'customer/order_list.html', {'orders': orders})


@login_required
@role_required('customer')
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, customer=request.user)
    can_review = order.status == 'delivered' and not hasattr(order, 'review')
    existing_review = getattr(order, 'review', None)
    status_order = ['pending', 'confirmed', 'preparing', 'ready', 'picked_up', 'on_the_way', 'delivered']
    try:
        current_index = status_order.index(order.status)
    except ValueError:
        current_index = -1
    tracking_steps = [
        ('pending', 'Placed', '📝'),
        ('confirmed', 'Confirmed', '✅'),
        ('preparing', 'Preparing', '👨‍🍳'),
        ('ready', 'Ready', '📦'),
        ('picked_up', 'Picked Up', '🛵'),
        ('on_the_way', 'On the Way', '🚗'),
        ('delivered', 'Delivered', '🎉'),
    ]
    return render(request, 'customer/order_detail.html', {
        'order': order,
        'can_review': can_review,
        'existing_review': existing_review,
        'tracking_steps': tracking_steps,
        'current_index': current_index,
    })


@login_required
@role_required('customer')
def add_review(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, customer=request.user, status='delivered')
    if hasattr(order, 'review'):
        messages.info(request, 'You have already reviewed this order.')
        return redirect('order_detail', order_id=order_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.order = order
            review.customer = request.user
            review.restaurant = order.restaurant
            review.save()
            messages.success(request, 'Thank you for your review!')
            return redirect('order_detail', order_id=order_id)
    else:
        form = ReviewForm()
    return render(request, 'customer/add_review.html', {'form': form, 'order': order})


# ==================== RESTAURANT VIEWS ====================

@login_required
@role_required('restaurant')
def restaurant_dashboard(request):
    restaurant = request.user.restaurant
    today = timezone.now().date()
    orders = restaurant.orders.all()
    stats = {
        'total_orders': orders.count(),
        'pending_orders': orders.filter(status='pending').count(),
        'today_orders': orders.filter(created_at__date=today).count(),
        'today_sales': orders.filter(created_at__date=today, status='delivered').aggregate(
            total=Sum('total'))['total'] or 0,
        'total_sales': orders.filter(status='delivered').aggregate(total=Sum('total'))['total'] or 0,
        'menu_count': restaurant.menu_items.count(),
    }
    recent_orders = orders[:5]
    return render(request, 'restaurant/dashboard.html', {
        'restaurant': restaurant,
        'stats': stats,
        'recent_orders': recent_orders,
    })


@login_required
@role_required('restaurant')
def restaurant_profile(request):
    restaurant = request.user.restaurant
    if request.method == 'POST':
        form = RestaurantProfileForm(request.POST, request.FILES, instance=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('restaurant_profile')
    else:
        form = RestaurantProfileForm(instance=restaurant)
    return render(request, 'restaurant/profile.html', {'form': form, 'restaurant': restaurant})


@login_required
@role_required('restaurant')
def manage_menu(request):
    restaurant = request.user.restaurant
    menu_items = restaurant.menu_items.select_related('category').all()
    categories = FoodCategory.objects.filter(is_active=True)
    return render(request, 'restaurant/menu.html', {
        'menu_items': menu_items,
        'categories': categories,
        'restaurant': restaurant,
    })


@login_required
@role_required('restaurant')
def add_menu_item(request):
    restaurant = request.user.restaurant
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.restaurant = restaurant
            item.save()
            messages.success(request, 'Menu item added successfully!')
            return redirect('manage_menu')
    else:
        form = FoodItemForm()
    return render(request, 'restaurant/menu_form.html', {'form': form, 'title': 'Add Menu Item'})


@login_required
@role_required('restaurant')
def edit_menu_item(request, pk):
    item = get_object_or_404(FoodItem, pk=pk, restaurant=request.user.restaurant)
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Menu item updated!')
            return redirect('manage_menu')
    else:
        form = FoodItemForm(instance=item)
    return render(request, 'restaurant/menu_form.html', {'form': form, 'title': 'Edit Menu Item'})


@login_required
@role_required('restaurant')
def delete_menu_item(request, pk):
    item = get_object_or_404(FoodItem, pk=pk, restaurant=request.user.restaurant)
    item.delete()
    messages.success(request, 'Menu item deleted.')
    return redirect('manage_menu')


@login_required
@role_required('restaurant')
def restaurant_orders(request):
    restaurant = request.user.restaurant
    status_filter = request.GET.get('status', '')
    orders = restaurant.orders.select_related('customer', 'delivery_partner').all()
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'restaurant/orders.html', {
        'orders': orders,
        'status_filter': status_filter,
        'status_choices': Order.STATUS_CHOICES,
    })


@login_required
@role_required('restaurant')
def update_order_status(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, restaurant=request.user.restaurant)
    new_status = request.POST.get('status')
    valid_statuses = ['confirmed', 'preparing', 'ready', 'rejected', 'cancelled']
    if new_status in valid_statuses:
        order.status = new_status
        order.save()
        send_order_notification(
            order,
            f'Order Update - #{order.order_id}',
            get_order_status_message(order),
        )
        messages.success(request, f'Order status updated to {order.get_status_display()}.')
    return redirect('restaurant_orders')


@login_required
@role_required('restaurant')
def restaurant_sales(request):
    restaurant = request.user.restaurant
    delivered = restaurant.orders.filter(status='delivered')
    stats = {
        'total_revenue': delivered.aggregate(total=Sum('total'))['total'] or 0,
        'total_orders': delivered.count(),
        'avg_order': delivered.aggregate(avg=Avg('total'))['avg'] or 0,
    }
    monthly = delivered.extra(
        select={'month': "strftime('%%Y-%%m', created_at)"}
    ).values('month').annotate(
        revenue=Sum('total'), count=Count('id')
    ).order_by('-month')[:6]
    return render(request, 'restaurant/sales.html', {
        'stats': stats,
        'monthly': monthly,
        'recent_orders': delivered[:10],
    })


# ==================== DELIVERY VIEWS ====================

@login_required
@role_required('delivery')
def delivery_dashboard(request):
    partner = request.user.delivery_partner
    active = partner.deliveries.filter(status__in=['ready', 'picked_up', 'on_the_way'])
    available = Order.objects.filter(status='ready', delivery_partner__isnull=True)
    stats = {
        'total_deliveries': partner.total_deliveries,
        'total_earnings': partner.total_earnings,
        'active_count': active.count(),
        'today_deliveries': partner.deliveries.filter(
            status='delivered', delivered_at__date=timezone.now().date()
        ).count(),
    }
    return render(request, 'delivery/dashboard.html', {
        'partner': partner,
        'active_deliveries': active,
        'available_orders': available[:5],
        'stats': stats,
    })


@login_required
@role_required('delivery')
def delivery_orders(request):
    partner = request.user.delivery_partner
    orders = partner.deliveries.all()
    available = Order.objects.filter(status='ready', delivery_partner__isnull=True)
    return render(request, 'delivery/orders.html', {
        'orders': orders,
        'available_orders': available,
    })


@login_required
@role_required('delivery')
def accept_delivery(request, order_id):
    partner = request.user.delivery_partner
    order = get_object_or_404(Order, order_id=order_id, status='ready', delivery_partner__isnull=True)
    order.delivery_partner = partner
    order.status = 'picked_up'
    order.save()
    send_order_notification(
        order,
        f'Delivery Partner Assigned - #{order.order_id}',
        get_order_status_message(order),
    )
    messages.success(request, f'Delivery accepted for order #{order.order_id}')
    return redirect('delivery_orders')


@login_required
@role_required('delivery')
def update_delivery_status(request, order_id):
    partner = request.user.delivery_partner
    order = get_object_or_404(Order, order_id=order_id, delivery_partner=partner)
    new_status = request.POST.get('status')
    if new_status in ['on_the_way', 'delivered']:
        order.status = new_status
        if new_status == 'delivered':
            order.delivered_at = timezone.now()
            partner.total_deliveries += 1
            earning = Decimal('50')
            partner.total_earnings += earning
            partner.save()
            if hasattr(order, 'payment') and order.payment.payment_method == 'cod':
                order.payment.status = 'completed'
                order.payment.save()
        order.save()
        send_order_notification(
            order,
            f'Order Update - #{order.order_id}',
            get_order_status_message(order),
        )
        messages.success(request, f'Status updated to {order.get_status_display()}.')
    return redirect('delivery_orders')


@login_required
@role_required('delivery')
def delivery_earnings(request):
    partner = request.user.delivery_partner
    deliveries = partner.deliveries.filter(status='delivered').order_by('-delivered_at')
    return render(request, 'delivery/earnings.html', {
        'partner': partner,
        'deliveries': deliveries,
    })


# ==================== ADMIN PANEL VIEWS ====================

@login_required
def admin_dashboard(request):
    if not (request.user.is_superuser or request.user.role == 'admin'):
        messages.error(request, 'Access denied.')
        return redirect('home')

    stats = {
        'total_users': User.objects.count(),
        'total_restaurants': Restaurant.objects.count(),
        'total_delivery': DeliveryPartner.objects.count(),
        'total_orders': Order.objects.count(),
        'total_revenue': Order.objects.filter(status='delivered').aggregate(total=Sum('total'))['total'] or 0,
        'pending_orders': Order.objects.filter(status='pending').count(),
    }
    recent_orders = Order.objects.select_related('customer', 'restaurant').order_by('-created_at')[:10]
    return render(request, 'admin_panel/dashboard.html', {
        'stats': stats,
        'recent_orders': recent_orders,
    })


@login_required
def admin_users(request):
    if not (request.user.is_superuser or request.user.role == 'admin'):
        return redirect('home')
    role_filter = request.GET.get('role', '')
    users = User.objects.all()
    if role_filter:
        users = users.filter(role=role_filter)
    return render(request, 'admin_panel/users.html', {'users': users, 'role_filter': role_filter})


@login_required
def admin_restaurants(request):
    if not (request.user.is_superuser or request.user.role == 'admin'):
        return redirect('home')
    restaurants = Restaurant.objects.select_related('user').all()
    return render(request, 'admin_panel/restaurants.html', {'restaurants': restaurants})


@login_required
def admin_toggle_restaurant(request, pk):
    if not (request.user.is_superuser or request.user.role == 'admin'):
        return redirect('home')
    restaurant = get_object_or_404(Restaurant, pk=pk)
    restaurant.is_approved = not restaurant.is_approved
    restaurant.save()
    messages.success(request, f'Restaurant {"approved" if restaurant.is_approved else "disapproved"}.')
    return redirect('admin_restaurants')


@login_required
def admin_delivery_partners(request):
    if not (request.user.is_superuser or request.user.role == 'admin'):
        return redirect('home')
    partners = DeliveryPartner.objects.select_related('user').all()
    return render(request, 'admin_panel/delivery_partners.html', {'partners': partners})


@login_required
def admin_orders(request):
    if not (request.user.is_superuser or request.user.role == 'admin'):
        return redirect('home')
    orders = Order.objects.select_related('customer', 'restaurant', 'delivery_partner').all()
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    return render(request, 'admin_panel/orders.html', {
        'orders': orders,
        'status_filter': status_filter,
        'status_choices': Order.STATUS_CHOICES,
    })


@login_required
def admin_categories(request):
    if not (request.user.is_superuser or request.user.role == 'admin'):
        return redirect('home')
    from .forms import CategoryForm
    categories = FoodCategory.objects.all()
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added!')
            return redirect('admin_categories')
    else:
        form = CategoryForm()
    return render(request, 'admin_panel/categories.html', {'categories': categories, 'form': form})


@login_required
def admin_coupons(request):
    if not (request.user.is_superuser or request.user.role == 'admin'):
        return redirect('home')
    coupons = Coupon.objects.all()
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon created!')
            return redirect('admin_coupons')
    else:
        form = CouponForm()
    return render(request, 'admin_panel/coupons.html', {'coupons': coupons, 'form': form})


@login_required
def admin_reports(request):
    if not (request.user.is_superuser or request.user.role == 'admin'):
        return redirect('home')

    total_revenue = Order.objects.filter(status='delivered').aggregate(total=Sum('total'))['total'] or 0
    orders_by_status = Order.objects.values('status').annotate(count=Count('id'))
    top_restaurants = Restaurant.objects.annotate(
        order_count=Count('orders'),
        revenue=Sum('orders__total')
    ).order_by('-revenue')[:5]

    monthly_revenue = Order.objects.filter(status='delivered').extra(
        select={'month': "strftime('%%Y-%%m', created_at)"}
    ).values('month').annotate(revenue=Sum('total')).order_by('-month')[:6]

    return render(request, 'admin_panel/reports.html', {
        'total_revenue': total_revenue,
        'orders_by_status': orders_by_status,
        'top_restaurants': top_restaurants,
        'monthly_revenue': monthly_revenue,
        'total_orders': Order.objects.count(),
        'total_customers': User.objects.filter(role='customer').count(),
    })
