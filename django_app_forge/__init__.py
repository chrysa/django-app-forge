"""django-app-forge — generate Django apps with a custom structure from YAML.

The core (``naming``, ``render``, ``spec``, ``generator``) is import-free of
Django so it can be unit-tested in isolation. Django is only imported by the
management command and the ``AppConfig``.
"""

from __future__ import annotations

__all__ = ["__version__"]

__version__ = "0.1.0"
