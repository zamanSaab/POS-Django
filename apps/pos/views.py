from decimal import Decimal
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView

from config.permissions import IsAdminOrStaff
from apps.dashboard.config import get_decimal_config
from apps.store.models import Product
from apps.orders.models import Order, OrderItem
from apps.orders.serializers import OrderSerializer
from apps.orders.views import build_initial_timeline
from .serializers import POSSaleCreateSerializer, ReceiptSerializer


class POSSaleView(APIView):
    permission_classes = [IsAdminOrStaff]

    def get(self, request):
        orders = Order.objects.filter(is_pos_sale=True).prefetch_related("items", "timeline").order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = POSSaleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        items_data = data["items"]
        product_ids = [i["product_id"] for i in items_data]
        products = {p.id: p for p in Product.objects.filter(id__in=product_ids)}

        errors = []
        for item in items_data:
            pid = item["product_id"]
            if pid not in products:
                errors.append(f"Product '{pid}' not found.")
            elif not products[pid].in_stock:
                errors.append(f"Product '{products[pid].name}' is out of stock.")
        if errors:
            return Response({"detail": errors}, status=status.HTTP_400_BAD_REQUEST)

        subtotal = sum(products[i["product_id"]].price * i["qty"] for i in items_data)
        discount_pct = Decimal(str(data.get("discount_percent", 0)))
        discount = subtotal * (discount_pct / 100)
        tax = (subtotal - discount) * get_decimal_config("TAX_RATE", "0.08")
        total = subtotal - discount + tax

        with transaction.atomic():
            order = Order.objects.create(
                user=None,
                customer_name=data.get("customer_name") or "Walk-in Customer",
                email="pos@frj-pos.com",
                phone="",
                shipping_address="In-Store",
                shipping_city="",
                shipping_zip="",
                payment_method=data["payment_method"],
                payment_status="confirmed",
                subtotal=subtotal,
                discount=discount,
                tax=tax,
                delivery_fee=Decimal("0"),
                total=total,
                is_pos_sale=True,
            )

            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    product=products[i["product_id"]],
                    name=products[i["product_id"]].name,
                    price=products[i["product_id"]].price,
                    qty=i["qty"],
                    variant=i.get("variant", ""),
                )
                for i in items_data
            ])
            build_initial_timeline(order)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class ReceiptView(RetrieveAPIView):
    permission_classes = [IsAdminOrStaff]
    serializer_class = ReceiptSerializer

    def get_object(self):
        order = Order.objects.prefetch_related("items").get(pk=self.kwargs["pk"], is_pos_sale=True)
        return order

    def retrieve(self, request, *args, **kwargs):
        order = self.get_object()
        data = {
            "order_number": order.order_number,
            "customer_name": order.customer_name,
            "payment_method": order.payment_method,
            "subtotal": order.subtotal,
            "discount": order.discount,
            "tax": order.tax,
            "total": order.total,
            "created_at": order.created_at,
            "items": order.items.all(),
        }
        serializer = self.get_serializer(data)
        return Response(serializer.data)
