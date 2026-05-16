from django.db import models


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
