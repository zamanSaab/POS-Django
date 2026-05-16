from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Phones load the app from http://<LAN-IP>:5173; match common private subnets (port 5173).
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^http://192\.168\.\d{1,3}\.\d{1,3}:5173$",
    r"^http://10\.\d{1,3}\.\d{1,3}\.\d{1,3}:5173$",
    r"^http://172\.(1[6-9]|2[0-9]|3[01])\.\d{1,3}\.\d{1,3}:5173$",
]

CORS_ALLOW_CREDENTIALS = True

