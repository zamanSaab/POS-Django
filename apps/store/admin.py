from django.contrib import admin
from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    fields = ["image", "is_primary", "order"]
    extra = 1
    ordering = ["-is_primary", "order"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "icon", "store_type"]
    list_filter = ["store_type"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "category", "price", "in_stock", "store_type"]
    list_filter = ["store_type", "in_stock", "category"]
    search_fields = ["name", "desc"]
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["id", "product", "is_primary", "order"]
    list_filter = ["is_primary"]
