"""Minimal Django settings for the test suite."""

import os

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-test-only")

INSTALLED_APPS = [
    "django_app_forge",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
