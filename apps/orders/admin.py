from django.contrib import admin
from .models import Order, OrderItem, OrderTimeline, SavedCart


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderTimelineInline(admin.TabularInline):
    model = OrderTimeline
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "customer_name", "status", "total", "payment_status", "is_pos_sale", "created_at"]
    list_filter = ["status", "payment_method", "payment_status", "is_pos_sale"]
    search_fields = ["order_number", "customer_name", "email"]
    inlines = [OrderItemInline, OrderTimelineInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "name", "price", "qty"]


@admin.register(OrderTimeline)
class OrderTimelineAdmin(admin.ModelAdmin):
    list_display = ["order", "step", "status", "time"]


@admin.register(SavedCart)
class SavedCartAdmin(admin.ModelAdmin):
    list_display = ["user", "updated_at"]
    search_fields = ["user__email", "user__name"]
