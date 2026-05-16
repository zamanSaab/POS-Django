from django.db import models, transaction


STORE_TYPE_CHOICES = [
    ("accessories", "Accessories"),
    ("clothing", "Clothing"),
    ("jewelry", "Jewelry"),
]


class Category(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=10)
    store_type = models.CharField(max_length=20, choices=STORE_TYPE_CHOICES)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return f"{self.name} ({self.store_type})"


class Product(models.Model):
    id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    reviews = models.IntegerField(default=0)
    in_stock = models.BooleanField(default=True)
    badge = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=20, default="#000000")
    desc = models.TextField(blank=True)
    variants = models.JSONField(default=list)
    store_type = models.CharField(max_length=20, choices=STORE_TYPE_CHOICES)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-is_primary", "order"]
        constraints = [
            models.UniqueConstraint(
                fields=["product"],
                condition=models.Q(is_primary=True),
                name="unique_primary_image_per_product",
            )
        ]

    def save(self, *args, **kwargs):
        if self.is_primary:
            with transaction.atomic():
                ProductImage.objects.filter(product=self.product, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        prefix = "[Primary] " if self.is_primary else ""
        return f"{prefix}{self.product.name} image {self.pk}"
