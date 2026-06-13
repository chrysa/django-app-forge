"""django-app-forge — generate Django apps with a custom structure from YAML.

The core (``naming``, ``render``, ``spec``, ``generator``) is import-free of
Django so it can be unit-tested in isolation. Django is only imported by the
management command and the ``AppConfig``.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("django-app-forge")
except PackageNotFoundError:  # editable install / not installed
    __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
