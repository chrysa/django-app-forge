"""Minimal Django settings for the django-app-forge demo project.

``django_app_forge`` is in ``INSTALLED_APPS`` so the ``forgeapps`` management
command is available. Everything else is the bare minimum to run management
commands.
"""

from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "demo-insecure-key-not-for-production"  # noqa: S105
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    # Provides the `forgeapps` management command.
    "django_app_forge",
]

MIDDLEWARE: list[str] = []
ROOT_URLCONF = "demo_project.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}

USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
