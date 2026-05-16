from django.urls import path
from .views import POSSaleView, ReceiptView

urlpatterns = [
    path("sales/", POSSaleView.as_view(), name="pos-sales"),
    path("sales/<int:pk>/receipt/", ReceiptView.as_view(), name="pos-receipt"),
]
