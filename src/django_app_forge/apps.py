from __future__ import annotations

from django.apps import AppConfig


class DjangoAppForgeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_app_forge"
    verbose_name = "Django App Forge"
