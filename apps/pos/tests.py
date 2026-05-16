from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.store.models import Category, Product

POS_URL = "/api/pos/sales/"


def make_staff():
    return User.objects.create_user(
        email="staff@luxepos.com",
        name="Staff User",
        password="testpass",
        role="staff",
    )


def make_product(pid="p1", name="Widget", price="10.00", in_stock=True):
    cat, _ = Category.objects.get_or_create(
        id="test-cat",
        defaults={"name": "Test", "icon": "🧪", "store_type": "accessories"},
    )
    product, _ = Product.objects.get_or_create(
        id=pid,
        defaults={
            "name": name,
            "category": cat,
            "price": price,
            "store_type": "accessories",
            "in_stock": in_stock,
        },
    )
    return product


VALID_PAYLOAD = {
    "items": [{"product_id": "p1", "qty": 1}],
    "payment_method": "card",
}


class POSEmptyItemsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(make_staff())

    def test_empty_items_returns_400(self):
        payload = {**VALID_PAYLOAD, "items": []}
        response = self.client.post(POS_URL, payload, format="json")
        self.assertEqual(response.status_code, 400)


class POSDiscountBoundsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(make_staff())
        make_product()

    def test_discount_above_100_returns_400(self):
        payload = {**VALID_PAYLOAD, "discount_percent": "150"}
        response = self.client.post(POS_URL, payload, format="json")
        self.assertEqual(response.status_code, 400)

    def test_negative_discount_returns_400(self):
        payload = {**VALID_PAYLOAD, "discount_percent": "-5"}
        response = self.client.post(POS_URL, payload, format="json")
        self.assertEqual(response.status_code, 400)


class POSOutOfStockTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(make_staff())
        make_product(pid="p1", in_stock=False)

    def test_out_of_stock_returns_400(self):
        response = self.client.post(POS_URL, VALID_PAYLOAD, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("out of stock", str(response.data).lower())


class POSUnknownProductTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(make_staff())

    def test_unknown_product_returns_400(self):
        payload = {**VALID_PAYLOAD, "items": [{"product_id": "ghost", "qty": 1}]}
        response = self.client.post(POS_URL, payload, format="json")
        self.assertEqual(response.status_code, 400)


class POSSuccessTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(make_staff())
        make_product(pid="p1", price="50.00")

    def test_valid_sale_creates_order_and_items(self):
        from apps.orders.models import Order, OrderItem
        response = self.client.post(POS_URL, VALID_PAYLOAD, format="json")
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data["order_number"].startswith("ORD-"))
        self.assertTrue(Order.objects.filter(order_number=data["order_number"]).exists())
        self.assertEqual(OrderItem.objects.filter(order__order_number=data["order_number"]).count(), 1)

    def test_unauthenticated_returns_401(self):
        unauthenticated = APIClient()
        response = unauthenticated.post(POS_URL, VALID_PAYLOAD, format="json")
        self.assertEqual(response.status_code, 401)
