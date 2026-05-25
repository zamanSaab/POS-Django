from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import User
from .admin import ConfigurationAdminForm
from .models import Configuration


class ConfigurationViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.config, _ = Configuration.objects.get_or_create(
            key=Configuration.ACTIVE_STORE_TYPE_KEY,
            defaults={"value": "accessories"},
        )

    def test_public_config_includes_active_storefront(self):
        response = self.client.get("/api/dashboard/config/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()[Configuration.ACTIVE_STORE_TYPE_KEY],
            "accessories",
        )

    def test_admin_form_renders_active_storefront_choices(self):
        form = ConfigurationAdminForm(instance=self.config)

        self.assertEqual(
            list(form.fields["value"].choices),
            Configuration.STORE_TYPE_CHOICES,
        )

    def test_admin_can_change_active_storefront(self):
        admin = User.objects.create_user(
            email="admin@example.com",
            name="Admin",
            password="secret123",
            role="admin",
        )
        self.client.force_authenticate(user=admin)

        response = self.client.patch(
            "/api/dashboard/config/",
            {Configuration.ACTIVE_STORE_TYPE_KEY: "jewelry"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.config.refresh_from_db()
        self.assertEqual(self.config.value, "jewelry")

    def test_admin_cannot_save_unknown_storefront(self):
        admin = User.objects.create_user(
            email="admin@example.com",
            name="Admin",
            password="secret123",
            role="admin",
        )
        self.client.force_authenticate(user=admin)

        response = self.client.patch(
            "/api/dashboard/config/",
            {Configuration.ACTIVE_STORE_TYPE_KEY: "invalid"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.config.refresh_from_db()
        self.assertEqual(self.config.value, "accessories")
