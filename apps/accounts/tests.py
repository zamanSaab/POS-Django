from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User


class RegisterCheckoutFieldsTest(TestCase):
    def test_register_accepts_phone_and_optional_shipping_fields(self):
        client = APIClient()
        payload = {
            "name": "Ali Khan",
            "email": "ali@example.com",
            "password": "secret123",
            "phone": "+92 300 1234567",
            "shipping_address": "House 12, Block B",
            "shipping_city": "Lahore",
            "shipping_zip": "54000",
        }

        response = client.post("/api/auth/register/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)
        self.assertEqual(data["user"]["name"], payload["name"])
        self.assertEqual(data["user"]["email"], payload["email"])
        self.assertEqual(data["user"]["phone"], payload["phone"])
        self.assertEqual(data["user"]["shipping_address"], payload["shipping_address"])
        self.assertEqual(data["user"]["shipping_city"], payload["shipping_city"])
        self.assertEqual(data["user"]["shipping_zip"], payload["shipping_zip"])

        user = User.objects.get(email=payload["email"])
        self.assertEqual(user.phone, payload["phone"])
        self.assertEqual(user.shipping_city, payload["shipping_city"])

    def test_me_includes_phone_and_shipping_fields(self):
        user = User.objects.create_user(
            email="customer@example.com",
            name="Customer",
            password="secret123",
            phone="+92 321 7654321",
            shipping_address="Street 5",
            shipping_city="Karachi",
            shipping_zip="74000",
        )
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get("/api/auth/me/")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["phone"], user.phone)
        self.assertEqual(data["shipping_address"], user.shipping_address)
        self.assertEqual(data["shipping_city"], user.shipping_city)
        self.assertEqual(data["shipping_zip"], user.shipping_zip)
