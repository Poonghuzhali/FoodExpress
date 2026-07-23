from django.contrib import admin
from .models import (
    User, FoodCategory, Restaurant, FoodItem, DeliveryPartner,
    Coupon, Cart, CartItem, Order, OrderItem, Payment, Review
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'phone', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'email']


@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active']
    search_fields = ['name']


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'cuisine_type', 'rating', 'is_open', 'is_approved']
    list_filter = ['is_open', 'is_approved', 'cuisine_type']
    search_fields = ['name']


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'category', 'price', 'is_available']
    list_filter = ['is_available', 'is_vegetarian', 'category']
    search_fields = ['name']


@admin.register(DeliveryPartner)
class DeliveryPartnerAdmin(admin.ModelAdmin):
    list_display = ['user', 'vehicle_type', 'is_available', 'total_deliveries', 'total_earnings']
    list_filter = ['is_available', 'is_approved']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'is_active', 'used_count']
    search_fields = ['code']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'customer', 'restaurant', 'status', 'total', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_id', 'customer__username']
    inlines = [OrderItemInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'order', 'payment_method', 'amount', 'status']
    list_filter = ['status', 'payment_method']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'customer', 'rating', 'created_at']
    list_filter = ['rating']
