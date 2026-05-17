from decimal import Decimal
from .models import Configuration


def get_config(key, default=""):
    try:
        return Configuration.objects.get(key=key).value
    except Configuration.DoesNotExist:
        return default


def get_decimal_config(key, default):
    return Decimal(get_config(key, str(default)))
