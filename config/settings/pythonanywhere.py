import os
from pathlib import Path
from .base import *

DEBUG = False

SECRET_KEY = os.environ["SECRET_KEY"]

ALLOWED_HOSTS = ["zaman07.pythonanywhere.com"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get("DB_NAME", "zaman07$luxepos"),
        "USER": os.environ.get("DB_USER", "zaman07"),
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ.get("DB_HOST", "zaman07.mysql.pythonanywhere-services.com"),
        "PORT": "3306",
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Insert WhiteNoise right after SecurityMiddleware
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Absolute path to the React production build (inside the Django project)
REACT_BUILD_DIR = BASE_DIR / "frontend"

CORS_ALLOWED_ORIGINS = [
    "https://zaman07.pythonanywhere.com",
]
CORS_ALLOW_CREDENTIALS = True
