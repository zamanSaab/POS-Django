from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.orders.models import Order, SavedCart
from apps.store.models import Category, Product


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


CHECKOUT_URL = "/api/orders/"

VALID_PAYLOAD = {
    "cart_items": [{"product_id": "p1", "qty": 1}],
    "customer_name": "Test User",
    "email": "test@example.com",
    "phone": "555-0100",
    "shipping_address": "1 Main St",
    "shipping_city": "Springfield",
    "shipping_zip": "12345",
    "payment_method": "card",
}


class CheckoutEmptyCartTest(TestCase):
    def test_empty_cart_returns_400(self):
        client = APIClient()
        payload = {**VALID_PAYLOAD, "cart_items": []}
        response = client.post(CHECKOUT_URL, payload, format="json")
        self.assertEqual(response.status_code, 400)


class CheckoutOutOfStockTest(TestCase):
    def setUp(self):
        make_product(pid="p1", in_stock=False)

    def test_out_of_stock_returns_400(self):
        client = APIClient()
        response = client.post(CHECKOUT_URL, VALID_PAYLOAD, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("out of stock", str(response.data).lower())


class CheckoutUnknownProductTest(TestCase):
    def test_unknown_product_returns_400(self):
        client = APIClient()
        payload = {**VALID_PAYLOAD, "cart_items": [{"product_id": "does-not-exist", "qty": 1}]}
        response = client.post(CHECKOUT_URL, payload, format="json")
        self.assertEqual(response.status_code, 400)


class AuthenticatedCartTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="cart@example.com",
            name="Cart User",
            password="secret123",
            phone="+92 300 1111111",
        )
        make_product(pid="p1", price="1500.00")
        make_product(pid="p2", name="Second Product", price="2500.00")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_put_get_and_delete_cart(self):
        put_response = self.client.put(
            "/api/cart/",
            {
                "cart_items": [
                    {"product_id": "p1", "quantity": 2, "variant": None},
                    {"product_id": "p2", "qty": 1, "variant": "Large"},
                ]
            },
            format="json",
        )

        self.assertEqual(put_response.status_code, 200)
        self.assertEqual(put_response.json()["cart_items"][0]["qty"], 2)

        get_response = self.client.get("/api/cart/")
        self.assertEqual(get_response.status_code, 200)
        items = get_response.json()["cart_items"]
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["product_id"], "p1")
        self.assertEqual(items[0]["product"]["name"], "Widget")
        self.assertIsNone(items[0]["variant"])

        delete_response = self.client.delete("/api/cart/")
        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(delete_response.json()["cart_items"], [])
        self.assertEqual(SavedCart.objects.get(user=self.user).cart_items, [])

    def test_post_aliases_put_cart_behavior(self):
        response = self.client.post(
            "/api/cart/",
            {"cart_items": [{"product_id": "p1", "qty": 3}]},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["cart_items"][0]["qty"], 3)


class CheckoutSuccessTest(TestCase):
    def setUp(self):
        make_product(pid="p1", price="20.00")

    def test_valid_order_created(self):
        client = APIClient()
        response = client.post(CHECKOUT_URL, VALID_PAYLOAD, format="json")
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data["order_number"].startswith("ORD-"))
        self.assertEqual(len(data["items"]), 1)

    def test_order_number_format(self):
        client = APIClient()
        response = client.post(CHECKOUT_URL, VALID_PAYLOAD, format="json")
        self.assertEqual(response.status_code, 201)
        # ORD- followed by 8 uppercase hex chars
        order_number = response.json()["order_number"]
        self.assertRegex(order_number, r"^ORD-[0-9A-F]{8}$")

    def test_quantity_fallback_creates_order_items(self):
        client = APIClient()
        payload = {**VALID_PAYLOAD, "cart_items": [{"product_id": "p1", "quantity": 2, "variant": None}]}

        response = client.post(CHECKOUT_URL, payload, format="json")

        self.assertEqual(response.status_code, 201)
        item = response.json()["items"][0]
        self.assertEqual(item["qty"], 2)
        self.assertIsNone(item["variant"])
        self.assertEqual(item["product"]["id"], "p1")

    def test_create_validation_errors_include_required_field_names(self):
        client = APIClient()
        response = client.post(CHECKOUT_URL, {}, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("cart_items", response.data)
        self.assertIn("customer_name", response.data)
        self.assertIn("email", response.data)
        self.assertIn("phone", response.data)
        self.assertIn("shipping_address", response.data)
        self.assertIn("shipping_city", response.data)
        self.assertIn("shipping_zip", response.data)

    def test_saved_cart_clears_after_authenticated_order(self):
        user = User.objects.create_user(
            email="buyer@example.com",
            name="Buyer",
            password="secret123",
            phone="+92 300 2222222",
        )
        SavedCart.objects.create(user=user, cart_items=[{"product_id": "p1", "qty": 1, "variant": None}])
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(CHECKOUT_URL, VALID_PAYLOAD, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(SavedCart.objects.get(user=user).cart_items, [])

    def test_get_orders_returns_logged_in_user_orders(self):
        user = User.objects.create_user(
            email="orders@example.com",
            name="Orders User",
            password="secret123",
            phone="+92 300 3333333",
        )
        client = APIClient()
        client.force_authenticate(user=user)
        create_response = client.post(CHECKOUT_URL, VALID_PAYLOAD, format="json")
        self.assertEqual(create_response.status_code, 201)

        list_response = client.get(CHECKOUT_URL)

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()), 1)
        self.assertEqual(list_response.json()[0]["email"], VALID_PAYLOAD["email"])


class CheckoutCollisionRetryTest(TestCase):
    def setUp(self):
        make_product(pid="p1", price="20.00")
        # Create the blocking order through save() so the patch controls its number.
        with patch("apps.orders.models.generate_order_number", return_value="ORD-AAAAAAAA"):
            Order.objects.create(
                customer_name="Existing", email="e@e.com", phone="",
                shipping_address="X", shipping_city="X", shipping_zip="0",
                payment_method="card", payment_status="confirmed",
                subtotal="20.00", discount="0", tax="1.60",
                delivery_fee="5.99", total="27.59",
            )

    def test_retry_succeeds_on_collision(self):
        client = APIClient()
        # First call returns the colliding number; second call returns a clean one.
        with patch("apps.orders.models.generate_order_number", side_effect=["ORD-AAAAAAAA", "ORD-BBBBBBBB"]):
            response = client.post(CHECKOUT_URL, VALID_PAYLOAD, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["order_number"], "ORD-BBBBBBBB")
