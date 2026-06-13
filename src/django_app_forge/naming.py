"""Name-derivation helpers (no Django, no third-party deps)."""

from __future__ import annotations

import re

_SPLIT = re.compile(r"[_\-\s]+")


def to_snake(name: str) -> str:
    """Normalize an app name to ``snake_case`` (``Api-Gateway`` -> ``api_gateway``)."""
    parts = [p for p in _SPLIT.split(name.strip()) if p]
    return "_".join(p.lower() for p in parts)


def to_pascal(name: str) -> str:
    """Convert an app name to ``PascalCase`` (``my_app`` -> ``MyApp``)."""
    parts = [p for p in _SPLIT.split(name.strip()) if p]
    return "".join(p[:1].upper() + p[1:] for p in parts)


def derived_context(app_name: str, base_path: str) -> dict[str, str]:
    """Build the per-app variables exposed to templates.

    ``base_path`` is the directory (relative to the generation root) the app
    lives in; it is used to compute the dotted Python module path.
    """
    snake = to_snake(app_name)
    segments = [s for s in re.split(r"[\\/]+", base_path.strip()) if s and s != "."]
    module = ".".join([*segments, snake])
    return {
        "app_name": snake,
        "app_label": snake,
        "app_class": to_pascal(app_name),
        "app_module": module,
    }
