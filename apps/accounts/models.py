from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("role", "admin")
        return self.create_user(email, name, password, **extra)


class User(AbstractUser):
    ROLE_CHOICES = [
        ("customer", "Customer"),
        ("admin", "Admin"),
        ("staff", "Staff"),
    ]

    username = None
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30, blank=True)
    shipping_address = models.CharField(max_length=500, blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_zip = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    def __str__(self):
        return self.email


class NotificationPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="notification_prefs")
    order_updates = models.BooleanField(default=True)
    promotions = models.BooleanField(default=True)
    stock_alerts = models.BooleanField(default=False)
    system_messages = models.BooleanField(default=True)

    def __str__(self):
        return f"Prefs for {self.user.email}"
