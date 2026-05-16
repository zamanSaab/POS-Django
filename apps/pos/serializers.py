from rest_framework import serializers
from apps.orders.serializers import OrderItemSerializer


class POSItemInputSerializer(serializers.Serializer):
    product_id = serializers.CharField()
    qty = serializers.IntegerField(min_value=1)
    variant = serializers.CharField(required=False, allow_blank=True, default="")


class POSSaleCreateSerializer(serializers.Serializer):
    items = POSItemInputSerializer(many=True, allow_empty=False)
    customer_name = serializers.CharField(required=False, allow_blank=True, default="Walk-in Customer")
    payment_method = serializers.ChoiceField(choices=["card", "cash", "wallet", "bank"])
    discount_percent = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, default=0,
        min_value=0, max_value=100,
    )


class ReceiptSerializer(serializers.Serializer):
    order_number = serializers.CharField()
    customer_name = serializers.CharField()
    payment_method = serializers.CharField()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount = serializers.DecimalField(max_digits=10, decimal_places=2)
    tax = serializers.DecimalField(max_digits=10, decimal_places=2)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    created_at = serializers.DateTimeField()
    items = OrderItemSerializer(many=True)
