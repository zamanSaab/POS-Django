import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from config.permissions import IsAdmin
from apps.dashboard.config import get_decimal_config
from apps.store.models import Product
from apps.notifications.models import Notification
from .emails import send_order_confirmation_email
from .models import Order, OrderItem, OrderTimeline, SavedCart
from .serializers import OrderCreateSerializer, OrderSerializer, SavedCartSerializer

VALID_COUPONS = {"LUXE10", "WELCOME10", "SAVE10"}

TIMELINE_STEPS = [
    ("Order Placed", "Your order has been confirmed."),
    ("Processing", "We are preparing your order."),
    ("Shipped", "Your order is on the way."),
    ("Out for Delivery", "Your order is out for delivery."),
    ("Delivered", "Order delivered successfully."),
]


def build_initial_timeline(order):
    entries = []
    for i, (step, detail) in enumerate(TIMELINE_STEPS):
        if i == 0:
            tl_status = "done"
            time = order.created_at
        elif i == 1:
            tl_status = "current"
            time = None
        else:
            tl_status = "pending"
            time = None
        entries.append(OrderTimeline(order=order, step=step, status=tl_status, time=time, detail=detail))
    OrderTimeline.objects.bulk_create(entries)


class OrderCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        orders = (
            Order.objects.filter(user=request.user)
            .select_related("user")
            .prefetch_related("items__product", "timeline")
            .order_by("-created_at")
        )
        return Response(OrderSerializer(orders, many=True).data)

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Validate products and compute subtotal from live DB prices
        cart_items = data["cart_items"]
        product_ids = [item["product_id"] for item in cart_items]
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}

        errors = []
        for item in cart_items:
            pid = item["product_id"]
            if pid not in products:
                errors.append(f"Product '{pid}' not found.")
            elif not products[pid].in_stock:
                errors.append(f"Product '{products[pid].name}' is out of stock.")
        if errors:
            return Response({"detail": errors}, status=status.HTTP_400_BAD_REQUEST)

        subtotal = sum(products[i["product_id"]].price * i["qty"] for i in cart_items)
        coupon = data.get("coupon_code", "").strip().upper()
        discount = subtotal * Decimal("0.10") if coupon in VALID_COUPONS else Decimal("0")
        delivery_fee = Decimal("0") if subtotal >= get_decimal_config("FREE_DELIVERY_THRESHOLD", "10000") \
            else get_decimal_config("DELIVERY_FEE", "250")
        tax = (subtotal - discount) * get_decimal_config("TAX_RATE", "0.08")
        total = subtotal - discount + tax + delivery_fee

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                customer_name=data["customer_name"],
                email=data["email"],
                phone=data["phone"],
                shipping_address=data["shipping_address"],
                shipping_city=data["shipping_city"],
                shipping_zip=data["shipping_zip"],
                payment_method=data["payment_method"],
                payment_status="confirmed" if data["payment_method"] != "cash" else "pending",
                subtotal=subtotal,
                discount=discount,
                tax=tax,
                delivery_fee=delivery_fee,
                total=total,
            )

            items_to_create = [
                OrderItem(
                    order=order,
                    product=products[item["product_id"]],
                    name=products[item["product_id"]].name,
                    price=products[item["product_id"]].price,
                    qty=item["qty"],
                    variant=item.get("variant") or "",
                )
                for item in cart_items
            ]
            OrderItem.objects.bulk_create(items_to_create)
            build_initial_timeline(order)

            if request.user.is_authenticated:
                SavedCart.objects.filter(user=request.user).update(cart_items=[])
                Notification.objects.create(
                    user=request.user,
                    type="order",
                    title="Order Placed",
                    body=f"Your order {order.order_number} has been placed successfully.",
                )

        try:
            send_order_confirmation_email(order)
        except Exception:
            logger.exception("Failed to send order confirmation email for order_id=%s", order.pk)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product", "timeline").order_by("-created_at")


class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product", "timeline")


class AdminOrderListView(generics.ListAPIView):
    permission_classes = [IsAdmin]
    serializer_class = OrderSerializer

    def get_queryset(self):
        qs = Order.objects.prefetch_related("items__product", "timeline").order_by("-created_at")
        params = self.request.query_params
        if s := params.get("status"):
            qs = qs.filter(status=s)
        if search := params.get("search"):
            qs = qs.filter(order_number__icontains=search) | qs.filter(customer_name__icontains=search)
        return qs


STATUS_STEP_MAP = {
    "processing": ("Processing", "We are preparing your order."),
    "shipped": ("Shipped", "Your order has been shipped."),
    "out_for_delivery": ("Out for Delivery", "Your order is out for delivery."),
    "delivered": ("Delivered", "Your order has been delivered."),
    "cancelled": ("Cancelled", "Your order has been cancelled."),
}

STATUS_TIMELINE_ORDER = ["processing", "shipped", "out_for_delivery", "delivered"]


def update_timeline_step(order, step, defaults):
    timelines = list(order.timeline.filter(step=step).order_by("id"))
    if not timelines:
        OrderTimeline.objects.create(order=order, step=step, **defaults)
        return

    timeline = timelines[0]
    for field, value in defaults.items():
        setattr(timeline, field, value)
    timeline.save(update_fields=[*defaults.keys()])
    duplicate_ids = [item.id for item in timelines[1:]]
    if duplicate_ids:
        OrderTimeline.objects.filter(id__in=duplicate_ids).delete()


def update_order_timeline(order, new_status):
    now = timezone.now()

    if new_status == "cancelled":
        update_timeline_step(
            order=order,
            step="Cancelled",
            defaults={
                "status": "current",
                "time": now,
                "detail": STATUS_STEP_MAP["cancelled"][1],
            },
        )
        order.timeline.exclude(step="Cancelled").filter(status="current").update(status="done")
        return

    current_index = STATUS_TIMELINE_ORDER.index(new_status)
    for index, status_key in enumerate(STATUS_TIMELINE_ORDER):
        step_label, detail = STATUS_STEP_MAP[status_key]
        if index < current_index:
            timeline_status = "done"
        elif index == current_index:
            timeline_status = "current" if new_status != "delivered" else "done"
        else:
            timeline_status = "pending"

        defaults = {
            "status": timeline_status,
            "detail": detail,
            "time": now if timeline_status in ("done", "current") else None,
        }
        update_timeline_step(order, step_label, defaults)

    order.timeline.filter(step="Cancelled").delete()


class OrderStatusUpdateView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        order.status = new_status
        order.save()

        update_order_timeline(order, new_status)

        if order.user:
            Notification.objects.create(
                user=order.user,
                type="order",
                title=f"Order {order.order_number} Update",
                body=f"Your order status has been updated to: {new_status.replace('_', ' ').title()}.",
            )

        return Response(OrderSerializer(order).data)


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get_cart(self, user):
        cart, _ = SavedCart.objects.get_or_create(user=user)
        return cart

    def get(self, request):
        cart = self.get_cart(request.user)
        return Response(SavedCartSerializer(cart).data)

    def put(self, request):
        cart = self.get_cart(request.user)
        serializer = SavedCartSerializer(cart, data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = serializer.save()
        return Response(SavedCartSerializer(cart).data)

    def post(self, request):
        return self.put(request)

    def delete(self, request):
        cart = self.get_cart(request.user)
        cart.cart_items = []
        cart.save(update_fields=["cart_items", "updated_at"])
        return Response({"cart_items": []})
