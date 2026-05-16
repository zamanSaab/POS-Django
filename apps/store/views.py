from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from config.permissions import IsAdmin
from .models import Category, Product
from .serializers import CategorySerializer, ProductListSerializer, ProductSerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related("category").all()

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return ProductSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdmin()]

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if store_type := params.get("store_type"):
            qs = qs.filter(store_type=store_type)
        if category := params.get("category"):
            qs = qs.filter(category_id=category)
        if in_stock := params.get("in_stock"):
            qs = qs.filter(in_stock=in_stock.lower() == "true")
        if search := params.get("search"):
            qs = qs.filter(name__icontains=search) | qs.filter(desc__icontains=search)
        return qs

    @action(detail=True, methods=["patch"], url_path="toggle-stock")
    def toggle_stock(self, request, pk=None):
        product = self.get_object()
        product.in_stock = not product.in_stock
        product.save()
        return Response({"id": product.id, "in_stock": product.in_stock})


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAdmin()]

    def get_queryset(self):
        qs = super().get_queryset()
        if store_type := self.request.query_params.get("store_type"):
            qs = qs.filter(store_type=store_type)
        return qs
