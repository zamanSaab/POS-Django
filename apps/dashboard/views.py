import calendar as cal_module
from datetime import datetime, timezone as dt_timezone
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView

from config.permissions import IsAdmin
from apps.accounts.models import User
from apps.accounts.serializers import UserSerializer
from apps.orders.models import Order, OrderItem
from apps.orders.serializers import OrderSerializer
from .models import Configuration


def pct_change(current, previous):
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(((current - previous) / previous) * 100, 1)


def month_range(year, month):
    first = datetime(year, month, 1, tzinfo=dt_timezone.utc)
    last_day = cal_module.monthrange(year, month)[1]
    last = datetime(year, month, last_day, 23, 59, 59, tzinfo=dt_timezone.utc)
    return first, last


def prev_month(year, month):
    if month == 1:
        return year - 1, 12
    return year, month - 1


class StatsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        now = timezone.now()
        cy, cm = now.year, now.month
        py, pm = prev_month(cy, cm)

        curr_start, curr_end = month_range(cy, cm)
        prev_start, prev_end = month_range(py, pm)

        curr_orders = Order.objects.filter(created_at__range=(curr_start, curr_end))
        prev_orders = Order.objects.filter(created_at__range=(prev_start, prev_end))

        curr_revenue = float(curr_orders.aggregate(s=Sum("total"))["s"] or 0)
        prev_revenue = float(prev_orders.aggregate(s=Sum("total"))["s"] or 0)

        curr_order_count = curr_orders.count()
        prev_order_count = prev_orders.count()

        total_customers = User.objects.filter(role="customer").count()
        new_curr = User.objects.filter(created_at__range=(curr_start, curr_end)).count()
        new_prev = User.objects.filter(created_at__range=(prev_start, prev_end)).count()

        curr_avg = float(curr_orders.aggregate(a=Avg("total"))["a"] or 0)
        prev_avg = float(prev_orders.aggregate(a=Avg("total"))["a"] or 0)

        return Response({
            "revenue": {
                "value": round(curr_revenue, 2),
                "change": pct_change(curr_revenue, prev_revenue),
            },
            "orders": {
                "value": curr_order_count,
                "change": pct_change(curr_order_count, prev_order_count),
            },
            "customers": {
                "total": total_customers,
                "new_this_month": new_curr,
                "change": pct_change(new_curr, new_prev),
            },
            "avg_order": {
                "value": round(curr_avg, 2),
                "change": pct_change(curr_avg, prev_avg),
            },
        })


class TopProductsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        top = (
            OrderItem.objects.values("product_id", "name")
            .annotate(units_sold=Sum("qty"))
            .order_by("-units_sold")[:5]
        )
        return Response(list(top))


class CustomerListView(ListAPIView):
    permission_classes = [IsAdmin]
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = User.objects.filter(role="customer").order_by("-created_at")
        if search := self.request.query_params.get("search"):
            qs = qs.filter(Q(name__icontains=search) | Q(email__icontains=search))
        return qs


class CustomerDetailView(RetrieveAPIView):
    permission_classes = [IsAdmin]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        orders = Order.objects.filter(user=user).prefetch_related("items", "timeline").order_by("-created_at")
        stats = orders.aggregate(
            total_orders=Count("id"),
            total_spent=Sum("total"),
            avg_order=Avg("total"),
        )
        return Response({
            "user": UserSerializer(user).data,
            "orders": OrderSerializer(orders, many=True).data,
            "stats": {
                "total_orders": stats["total_orders"] or 0,
                "total_spent": float(stats["total_spent"] or 0),
                "avg_order": float(stats["avg_order"] or 0),
            },
        })


class ReportsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        from django.db.models.functions import TruncMonth
        monthly = (
            Order.objects.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(revenue=Sum("total"), orders=Count("id"))
            .order_by("month")
        )
        by_store_type = (
            OrderItem.objects.values("product__store_type")
            .annotate(units=Sum("qty"), revenue=Sum(F("price") * F("qty")))
            .order_by("-revenue")
        )
        return Response({
            "monthly": list(monthly),
            "by_store_type": list(by_store_type),
        })


class ConfigView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            obj.key: obj.value
            for obj in Configuration.objects.all()
        })

    def patch(self, request):
        self.permission_classes = [IsAdmin]
        self.check_permissions(request)
        updated = {}
        for key, value in request.data.items():
            rows = Configuration.objects.filter(key=key)
            if rows.exists():
                rows.update(value=str(value))
                updated[key] = str(value)
        return Response(updated)
