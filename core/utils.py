from django.core.mail import send_mail
from django.conf import settings


def send_order_confirmation_email(order, payment=None):
    """Send detailed order confirmation email to the customer who placed the order."""
    customer = order.customer
    if not customer.email:
        return False

    items_lines = []
    for item in order.items.all():
        items_lines.append(f"  • {item.quantity}x {item.food_name} — ₹{item.subtotal}")

    payment_info = 'Cash on Delivery (pay when delivered)'
    if payment:
        if payment.payment_method == 'card':
            card_num = getattr(payment, '_card_number', None)
            if card_num:
                payment_info = f"Card ending {card_num[-4:]} — Paid ₹{payment.amount}"
            else:
                payment_info = f"Credit/Debit Card — Paid ₹{payment.amount}"
        elif payment.payment_method == 'upi':
            payment_info = f"UPI — Paid ₹{payment.amount}"
        elif payment.payment_method == 'wallet':
            payment_info = f"Wallet — Paid ₹{payment.amount}"
        else:
            payment_info = f"{payment.get_payment_method_display()} — ₹{payment.amount}"

    message = f"""Hello {customer.first_name or customer.username},

Thank you for ordering from FoodExpress! Your order has been confirmed.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ORDER CONFIRMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Order ID:     {order.order_id}
Restaurant:   {order.restaurant.name}
Status:       {order.get_status_display()}
Placed on:    {order.created_at.strftime('%B %d, %Y at %I:%M %p')}

DELIVERY DETAILS
────────────────
Address:  {order.delivery_address}
Phone:    {order.delivery_phone}
"""
    if order.special_instructions:
        message += f"Notes:    {order.special_instructions}\n"

    message += f"""
ORDER ITEMS
────────────────
{chr(10).join(items_lines)}

PAYMENT SUMMARY
────────────────
Subtotal:      ₹{order.subtotal}
"""
    if order.discount:
        message += f"Discount:      -₹{order.discount}\n"
    message += f"""Delivery Fee:  ₹{order.delivery_fee}
Tax:           ₹{order.tax}
────────────────
TOTAL:         ₹{order.total}

Payment:       {payment_info}
"""
    if payment and payment.transaction_id:
        message += f"Transaction:   {payment.transaction_id}\n"

    message += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Track your order anytime by logging into FoodExpress.

After delivery, you can rate your experience and leave a review!

Thank you for choosing FoodExpress.
— The FoodExpress Team
"""

    try:
        send_mail(
            subject=f'Order Confirmed — #{order.order_id} | FoodExpress',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[customer.email],
            fail_silently=False,
        )
        return True
    except Exception:
        return False


def send_order_notification(order, subject, message):
    """Send status update email to customer."""
    if not order.customer.email:
        return
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer.email],
            fail_silently=True,
        )
        if order.restaurant.email:
            send_mail(
                subject=f"New Order #{order.order_id}",
                message=f"You have a new order from {order.customer.username}.\nTotal: ₹{order.total}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.restaurant.email],
                fail_silently=True,
            )
    except Exception:
        pass


def get_order_status_message(order):
    return (
        f"Order #{order.order_id} Update\n\n"
        f"Status: {order.get_status_display()}\n"
        f"Restaurant: {order.restaurant.name}\n"
        f"Total: ₹{order.total}\n\n"
        f"Track your order at FoodExpress!"
    )
