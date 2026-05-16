from rest_framework import serializers
from apps.store.models import Product
from apps.store.serializers import ProductListSerializer
from .models import Order, OrderItem, OrderTimeline, SavedCart


class OrderItemSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    variant = serializers.SerializerMethodField()
    product = ProductListSerializer(read_only=True)

    def get_variant(self, obj):
        return obj.variant or None

    class Meta:
        model = OrderItem
        fields = ["id", "product_id", "name", "price", "qty", "variant", "product"]


class OrderTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTimeline
        fields = ["id", "step", "status", "time", "detail"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    order_items = OrderItemSerializer(source="items", many=True, read_only=True)
    timeline = OrderTimelineSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    discount = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    tax = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    delivery_fee = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    shipping_cost = serializers.DecimalField(source="delivery_fee", max_digits=10, decimal_places=2, coerce_to_string=False, read_only=True)
    delivery = serializers.DecimalField(source="delivery_fee", max_digits=10, decimal_places=2, coerce_to_string=False, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = Order
        fields = [
            "id", "order_number", "user_id", "customer_name", "email", "phone",
            "status", "payment_method", "payment_status",
            "subtotal", "discount", "tax", "delivery_fee", "shipping_cost", "delivery", "total",
            "shipping_address", "shipping_city", "shipping_zip",
            "created_at", "is_pos_sale", "items", "order_items", "timeline",
        ]


class CartItemInputSerializer(serializers.Serializer):
    product_id = serializers.CharField()
    qty = serializers.IntegerField(min_value=1, required=False)
    quantity = serializers.IntegerField(min_value=1, required=False)
    variant = serializers.CharField(required=False, allow_blank=True, allow_null=True, default=None)

    def validate(self, attrs):
        qty = attrs.get("qty", attrs.get("quantity"))
        if qty is None:
            raise serializers.ValidationError({"qty": "This field is required."})
        attrs["qty"] = qty
        return attrs


class OrderCreateSerializer(serializers.Serializer):
    cart_items = CartItemInputSerializer(many=True, allow_empty=False)
    customer_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    shipping_address = serializers.CharField()
    shipping_city = serializers.CharField()
    shipping_zip = serializers.CharField()
    payment_method = serializers.ChoiceField(choices=["card", "cash", "wallet", "bank"])
    coupon_code = serializers.CharField(required=False, allow_blank=True, default="")


class SavedCartSerializer(serializers.ModelSerializer):
    cart_items = CartItemInputSerializer(many=True, allow_empty=True)

    class Meta:
        model = SavedCart
        fields = ["cart_items"]

    def validate_cart_items(self, value):
        product_ids = [item["product_id"] for item in value]
        existing_ids = set(Product.objects.filter(id__in=product_ids).values_list("id", flat=True))
        missing_ids = [pid for pid in product_ids if pid not in existing_ids]
        if missing_ids:
            raise serializers.ValidationError([f"Product '{pid}' not found." for pid in missing_ids])
        return value

    def to_representation(self, instance):
        product_ids = [item.get("product_id") for item in instance.cart_items]
        products = {
            product.id: product
            for product in Product.objects.filter(id__in=product_ids)
        }
        return {
            "cart_items": [
                {
                    "product_id": item.get("product_id"),
                    "qty": item.get("qty", item.get("quantity")),
                    "variant": item.get("variant"),
                    "product": ProductListSerializer(products[item.get("product_id")]).data
                    if item.get("product_id") in products else None,
                }
                for item in instance.cart_items
            ]
        }

    def update(self, instance, validated_data):
        instance.cart_items = [
            {
                "product_id": item["product_id"],
                "qty": item["qty"],
                "variant": item.get("variant"),
            }
            for item in validated_data["cart_items"]
        ]
        instance.save(update_fields=["cart_items", "updated_at"])
        return instance
