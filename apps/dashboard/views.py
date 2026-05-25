import calendar as cal_module
from datetime import datetime, timedelta, timezone as dt_timezone
from django.db.models import Sum, Count, Avg, Q, F
from django.db.models.functions import TruncDate
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
from apps.store.models import Product
from .models import Configuration, SiteVisit


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
        today = now.date()
        cy, cm = now.year, now.month
        py, pm = prev_month(cy, cm)

        curr_start, curr_end = month_range(cy, cm)
        prev_start, prev_end = month_range(py, pm)

        # ── Revenue ──
        curr_orders = Order.objects.filter(created_at__range=(curr_start, curr_end))
        prev_orders = Order.objects.filter(created_at__range=(prev_start, prev_end))
        curr_revenue = float(curr_orders.aggregate(s=Sum("total"))["s"] or 0)
        prev_revenue = float(prev_orders.aggregate(s=Sum("total"))["s"] or 0)

        # ── Orders ──
        curr_order_count = curr_orders.count()
        prev_order_count = prev_orders.count()
        pending_count = Order.objects.filter(status="processing").count()
        completed_count = Order.objects.filter(status="delivered").count()
        cancelled_count = Order.objects.filter(status="cancelled").count()
        total_order_count = Order.objects.count()

        # ── Customers ──
        week_ago = today - timedelta(days=6)
        month_start = today.replace(day=1)
        total_customers = User.objects.filter(role="customer").count()
        new_curr = User.objects.filter(created_at__range=(curr_start, curr_end)).count()
        new_prev = User.objects.filter(created_at__range=(prev_start, prev_end)).count()
        new_today = User.objects.filter(role="customer", created_at__date=today).count()
        new_week = User.objects.filter(role="customer", created_at__date__gte=week_ago).count()

        # ── Avg order ──
        curr_avg = float(curr_orders.aggregate(a=Avg("total"))["a"] or 0)
        prev_avg = float(prev_orders.aggregate(a=Avg("total"))["a"] or 0)

        # ── Products ──
        total_products = Product.objects.count()
        out_of_stock = Product.objects.filter(in_stock=False).count()

        # ── Weekly chart (last 7 days, gaps filled with 0) ──
        week_start = today - timedelta(days=6)
        daily_qs = (
            Order.objects.filter(created_at__date__gte=week_start)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(rev=Sum("total"))
            .order_by("day")
        )
        rev_map = {row["day"]: float(row["rev"]) for row in daily_qs}
        DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        weekly_chart = [
            {
                "label": DAY_LABELS[(week_start + timedelta(days=i)).weekday()],
                "value": rev_map.get(week_start + timedelta(days=i), 0.0),
            }
            for i in range(7)
        ]

        # ── Recent orders (last 8) ──
        recent_qs = Order.objects.prefetch_related("items").order_by("-created_at")[:8]
        recent_orders = [
            {
                "id": o.order_number,
                "customer": o.customer_name,
                "items": o.items.count(),
                "total": float(o.total),
                "status": o.status,
                "date": o.created_at.strftime("%b %d, %Y"),
                "payment": o.payment_method,
            }
            for o in recent_qs
        ]

        # ── Recent users (last 5 customers) ──
        recent_users = [
            {
                "id": u["id"],
                "name": u["name"],
                "email": u["email"],
                "created_at": u["created_at"].strftime("%b %d, %Y") if u["created_at"] else "",
            }
            for u in User.objects.filter(role="customer")
            .order_by("-created_at")[:5]
            .values("id", "name", "email", "created_at")
        ]

        # ── Best selling products (top 5 by units sold) ──
        best_selling = list(
            OrderItem.objects.values("product_id", "name")
            .annotate(units_sold=Sum("qty"))
            .order_by("-units_sold")[:5]
        )

        # ── Visitors ──
        visitors_today = SiteVisit.objects.filter(date=today).count()
        visitors_week = SiteVisit.objects.filter(date__gte=week_ago).count()
        visitors_month = SiteVisit.objects.filter(date__gte=month_start).count()
        visitors_total = SiteVisit.objects.count()

        return Response({
            "revenue": {
                "value": round(curr_revenue, 2),
                "change": pct_change(curr_revenue, prev_revenue),
                "period": "vs last month",
            },
            "orders": {
                "value": curr_order_count,
                "change": pct_change(curr_order_count, prev_order_count),
                "period": "vs last month",
                "total": total_order_count,
                "pending": pending_count,
                "completed": completed_count,
                "cancelled": cancelled_count,
            },
            "customers": {
                "value": total_customers,
                "change": pct_change(new_curr, new_prev),
                "period": "new this month",
                "new_today": new_today,
                "new_week": new_week,
                "new_month": new_curr,
            },
            "avg_order": {
                "value": round(curr_avg, 2),
                "change": pct_change(curr_avg, prev_avg),
                "period": "vs last month",
            },
            "products": {
                "total": total_products,
                "out_of_stock": out_of_stock,
            },
            "visitors": {
                "today": visitors_today,
                "week": visitors_week,
                "month": visitors_month,
                "total": visitors_total,
            },
            "weekly_chart": weekly_chart,
            "recent_orders": recent_orders,
            "recent_users": recent_users,
            "best_selling": best_selling,
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
        qs = (
            User.objects.filter(role="customer")
            .annotate(
                total_orders=Count("orders", distinct=True),
                total_spent=Sum("orders__total"),
            )
            .order_by("-created_at")
        )
        if search := self.request.query_params.get("search"):
            qs = qs.filter(Q(name__icontains=search) | Q(email__icontains=search))
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        items = page if page is not None else queryset
        cutoff = timezone.now() - timedelta(days=30)
        data = []
        for u in items:
            orders = getattr(u, "total_orders", 0) or 0
            spent = float(getattr(u, "total_spent", 0) or 0)
            if spent > 500 or orders > 5:
                tag = "VIP"
            elif u.created_at >= cutoff:
                tag = "New"
            else:
                tag = "Regular"
            data.append({
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "phone": u.phone or "",
                "orders": orders,
                "spent": round(spent, 2),
                "joined": u.created_at.strftime("%b %d, %Y"),
                "tag": tag,
            })
        if page is not None:
            return self.get_paginated_response(data)
        return Response(data)


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
