from django.db import migrations

DEFAULT_CONFIG = [
    ("CURRENCY",               "PKR",    "Currency symbol/code shown in emails and UI"),
    ("DELIVERY_FEE",           "250",    "Flat delivery fee in PKR when order is below the free-delivery threshold"),
    ("FREE_DELIVERY_THRESHOLD","10000",  "Order subtotal (PKR) at or above which delivery is free"),
    ("TAX_RATE",               "0.08",   "Tax rate as a decimal fraction, e.g. 0.08 = 8%"),
]


def seed_config(apps, schema_editor):
    Configuration = apps.get_model("dashboard", "Configuration")
    for key, value, description in DEFAULT_CONFIG:
        Configuration.objects.get_or_create(key=key, defaults={"value": value, "description": description})


def unseed_config(apps, schema_editor):
    Configuration = apps.get_model("dashboard", "Configuration")
    Configuration.objects.filter(key__in=[row[0] for row in DEFAULT_CONFIG]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_config, reverse_code=unseed_config),
    ]
