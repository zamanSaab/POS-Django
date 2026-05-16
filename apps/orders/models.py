import uuid
from django.conf import settings
from django.db import IntegrityError, models, transaction


def generate_order_number():
    token = uuid.uuid4().hex[:8].upper()
    return f"ORD-{token}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    PAYMENT_METHOD_CHOICES = [
        ("card", "Card"),
        ("cash", "Cash"),
        ("wallet", "Wallet"),
        ("bank", "Bank"),
    ]
    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("failed", "Failed"),
    ]

    order_number = models.CharField(max_length=20, unique=True, default=generate_order_number)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )
    customer_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="processing")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default="card")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.CharField(max_length=500)
    shipping_city = models.CharField(max_length=100)
    shipping_zip = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    is_pos_sale = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self._state.adding:
            super().save(*args, **kwargs)
            return
        # Always call through the module namespace so tests can patch generate_order_number.
        # The field default is overwritten here on every attempt (including the first).
        self.order_number = generate_order_number()
        for _ in range(5):
            try:
                with transaction.atomic():
                    super().save(*args, **kwargs)
                return
            except IntegrityError:
                self.order_number = generate_order_number()
        raise IntegrityError("Unable to generate a unique order number after 5 attempts.")

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "store.Product", on_delete=models.SET_NULL, null=True, related_name="order_items"
    )
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    qty = models.IntegerField()
    variant = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name} x{self.qty}"


class OrderTimeline(models.Model):
    TIMELINE_STATUS_CHOICES = [
        ("done", "Done"),
        ("current", "Current"),
        ("pending", "Pending"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="timeline")
    step = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=TIMELINE_STATUS_CHOICES, default="pending")
    time = models.DateTimeField(null=True, blank=True)
    detail = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f"{self.order.order_number} — {self.step}"


class SavedCart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_cart")
    cart_items = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.email}"
