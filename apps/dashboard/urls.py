from django.urls import path
from .views import (
    CustomerDetailView,
    CustomerListView,
    ReportsView,
    StatsView,
    TopProductsView,
)

urlpatterns = [
    path("stats/", StatsView.as_view(), name="dashboard-stats"),
    path("top-products/", TopProductsView.as_view(), name="dashboard-top-products"),
    path("customers/", CustomerListView.as_view(), name="dashboard-customers"),
    path("customers/<int:pk>/", CustomerDetailView.as_view(), name="dashboard-customer-detail"),
    path("reports/", ReportsView.as_view(), name="dashboard-reports"),
]
