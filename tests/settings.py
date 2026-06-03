"""Minimal Django settings for the test suite."""

SECRET_KEY = "test-only-not-secret"  # noqa: S105

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
