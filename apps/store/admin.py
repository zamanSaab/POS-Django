from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "icon", "store_type"]
    list_filter = ["store_type"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "category", "price", "in_stock", "store_type"]
    list_filter = ["store_type", "in_stock", "category"]
    search_fields = ["name", "desc"]
