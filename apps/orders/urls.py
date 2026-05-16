from django.urls import path
from .views import (
    AdminOrderListView,
    OrderCreateView,
    OrderDetailView,
    OrderListView,
    OrderStatusUpdateView,
)

urlpatterns = [
    path("", OrderCreateView.as_view(), name="order-create"),
    path("my/", OrderListView.as_view(), name="order-list"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("admin/", AdminOrderListView.as_view(), name="admin-order-list"),
    path("<int:pk>/status/", OrderStatusUpdateView.as_view(), name="order-status-update"),
]
