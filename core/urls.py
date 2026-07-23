from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.home, name='home'),
    path('restaurants/', views.restaurant_list, name='restaurant_list'),
    path('restaurants/<int:pk>/', views.restaurant_detail, name='restaurant_detail'),
    path('search/', views.search, name='search'),

    # Auth
    path('register/', views.register_customer, name='register'),
    path('register/restaurant/', views.register_restaurant, name='register_restaurant'),
    path('register/delivery/', views.register_delivery, name='register_delivery'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Customer
    path('profile/', views.customer_profile, name='customer_profile'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<str:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<str:order_id>/review/', views.add_review, name='add_review'),

    # Restaurant
    path('restaurant/dashboard/', views.restaurant_dashboard, name='restaurant_dashboard'),
    path('restaurant/profile/', views.restaurant_profile, name='restaurant_profile'),
    path('restaurant/menu/', views.manage_menu, name='manage_menu'),
    path('restaurant/menu/add/', views.add_menu_item, name='add_menu_item'),
    path('restaurant/menu/<int:pk>/edit/', views.edit_menu_item, name='edit_menu_item'),
    path('restaurant/menu/<int:pk>/delete/', views.delete_menu_item, name='delete_menu_item'),
    path('restaurant/orders/', views.restaurant_orders, name='restaurant_orders'),
    path('restaurant/orders/<str:order_id>/update/', views.update_order_status, name='update_order_status'),
    path('restaurant/sales/', views.restaurant_sales, name='restaurant_sales'),

    # Delivery
    path('delivery/dashboard/', views.delivery_dashboard, name='delivery_dashboard'),
    path('delivery/orders/', views.delivery_orders, name='delivery_orders'),
    path('delivery/accept/<str:order_id>/', views.accept_delivery, name='accept_delivery'),
    path('delivery/update/<str:order_id>/', views.update_delivery_status, name='update_delivery_status'),
    path('delivery/earnings/', views.delivery_earnings, name='delivery_earnings'),

    # Admin Panel
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/restaurants/', views.admin_restaurants, name='admin_restaurants'),
    path('admin-panel/restaurants/<int:pk>/toggle/', views.admin_toggle_restaurant, name='admin_toggle_restaurant'),
    path('admin-panel/delivery/', views.admin_delivery_partners, name='admin_delivery_partners'),
    path('admin-panel/orders/', views.admin_orders, name='admin_orders'),
    path('admin-panel/categories/', views.admin_categories, name='admin_categories'),
    path('admin-panel/coupons/', views.admin_coupons, name='admin_coupons'),
    path('admin-panel/reports/', views.admin_reports, name='admin_reports'),
]
