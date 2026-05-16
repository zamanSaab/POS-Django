from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.test import TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient
from unittest.mock import patch

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


class PasswordResetTest(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="customer@example.com",
            name="Customer",
            password="secret123",
        )

    @patch("apps.accounts.views.send_mail", side_effect=RuntimeError("SMTP unavailable"))
    def test_password_reset_request_returns_generic_response_when_email_fails(self, mocked_send_mail):
        response = self.client.post(
            "/api/auth/password-reset/",
            {"email": self.user.email},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"detail": "If that email exists, a reset link has been sent."})
        mocked_send_mail.assert_called_once()

    @patch("apps.accounts.views.send_mail")
    def test_password_reset_request_returns_same_response_for_unknown_email(self, mocked_send_mail):
        response = self.client.post(
            "/api/auth/password-reset/",
            {"email": "missing@example.com"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"detail": "If that email exists, a reset link has been sent."})
        mocked_send_mail.assert_not_called()

    def test_password_reset_confirm_rejects_malformed_uid(self):
        response = self.client.post(
            "/api/auth/password-reset/confirm/",
            {"uid": "***not-base64***", "token": "bad-token", "new_password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Invalid reset link."})

    def test_password_reset_confirm_uses_password_validators(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        response = self.client.post(
            "/api/auth/password-reset/confirm/",
            {"uid": uid, "token": token, "new_password": "password"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("new_password", response.json())

    @patch("apps.accounts.views.send_mail")
    def test_password_reset_request_is_throttled(self, mocked_send_mail):
        for _ in range(5):
            response = self.client.post(
                "/api/auth/password-reset/",
                {"email": "missing@example.com"},
                format="json",
            )
            self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/api/auth/password-reset/",
            {"email": "missing@example.com"},
            format="json",
        )

        self.assertEqual(response.status_code, 429)
