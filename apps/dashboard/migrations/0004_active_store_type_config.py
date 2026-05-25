from django.db import migrations


def seed_active_store_type(apps, schema_editor):
    Configuration = apps.get_model("dashboard", "Configuration")
    Configuration.objects.get_or_create(
        key="ACTIVE_STORE_TYPE",
        defaults={
            "value": "accessories",
            "description": "Storefront shown to site visitors: accessories, clothing, or jewelry",
        },
    )


def unseed_active_store_type(apps, schema_editor):
    Configuration = apps.get_model("dashboard", "Configuration")
    Configuration.objects.filter(key="ACTIVE_STORE_TYPE").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0003_sitevisit"),
    ]

    operations = [
        migrations.RunPython(seed_active_store_type, reverse_code=unseed_active_store_type),
    ]
