from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "icon", "store_type"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Product
        fields = [
            "id", "name", "category", "category_id", "price", "old_price",
            "rating", "reviews", "in_stock", "badge", "color", "desc",
            "variants", "store_type",
        ]

    def create(self, validated_data):
        category_id = validated_data.pop("category_id", None)
        if category_id:
            validated_data["category_id"] = category_id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        category_id = validated_data.pop("category_id", None)
        if category_id:
            validated_data["category_id"] = category_id
        return super().update(instance, validated_data)


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id", "name", "category_id", "price", "old_price",
            "rating", "in_stock", "badge", "color", "store_type",
        ]
