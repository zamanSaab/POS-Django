from django.conf import settings
from django.core.mail import send_mail

from apps.dashboard.config import get_config


def send_order_confirmation_email(order):
    if order.email == "pos@frj-pos.com":
        return
    currency = get_config("CURRENCY", "PKR")
    order_url = f"{settings.FRONTEND_URL}?order={order.order_number}"
    send_mail(
        subject=f"Order Confirmed — {order.order_number}",
        message=(
            f"Hi {order.customer_name},\n\n"
            f"Your order {order.order_number} has been placed successfully.\n\n"
            f"  Subtotal:      {currency} {order.subtotal}\n"
            f"  Discount:      {currency} {order.discount}\n"
            f"  Tax (8%):      {currency} {order.tax}\n"
            f"  Delivery:      {currency} {order.delivery_fee}\n"
            f"  ─────────────────────────\n"
            f"  Total:         {currency} {order.total}\n\n"
            f"View your order here:\n{order_url}\n\n"
            f"— The FRJ-POS Team"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        fail_silently=True,
    )
