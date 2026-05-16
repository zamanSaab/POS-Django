from rest_framework import serializers
from .models import Category, Product, ProductImage

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "icon", "store_type"]


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["id", "image_url", "is_primary", "order"]

    def get_image_url(self, obj):
        if not obj.image:
            return None
        url = obj.image.url
        request = self.context.get("request")
        if request and not url.startswith("http"):
            return request.build_absolute_uri(url)
        return url


class ProductImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "product", "image", "is_primary", "order"]

    def validate_image(self, value):
        if value.size > MAX_IMAGE_SIZE:
            raise serializers.ValidationError("Image must be under 5 MB.")
        if value.content_type not in ALLOWED_IMAGE_TYPES:
            raise serializers.ValidationError("Only JPEG, PNG, and WebP images are allowed.")
        return value

    def to_representation(self, instance):
        return ProductImageSerializer(instance, context=self.context).data


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.CharField(write_only=True, required=False)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "category", "category_id", "price", "old_price",
            "rating", "reviews", "in_stock", "badge", "color", "desc",
            "variants", "store_type", "images",
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
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "category_id", "price", "old_price",
            "rating", "in_stock", "badge", "color", "store_type", "primary_image",
        ]

    def get_primary_image(self, obj):
        all_images = obj.images.all()  # uses prefetch_related cache — no extra query
        img = next((i for i in all_images if i.is_primary), None) or next(iter(all_images), None)
        if not img:
            return None
        url = img.image.url
        request = self.context.get("request")
        if request and not url.startswith("http"):
            return request.build_absolute_uri(url)
        return url
