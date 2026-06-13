"""Minimal ``{{ variable }}`` substitution (no Jinja dependency)."""

from __future__ import annotations

import re
from collections.abc import Mapping

_PLACEHOLDER = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")


class RenderError(ValueError):
    """Raised when a template references a variable absent from the context."""


def render(template: str, context: Mapping[str, str]) -> str:
    """Replace every ``{{ name }}`` in *template* with ``context[name]``.

    Raises :class:`RenderError` (listing the offending name and the available
    keys) if a referenced variable is missing — fail loud, never silently emit
    a literal ``{{ ... }}`` into a generated file.
    """

    def _sub(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in context:
            available = ", ".join(sorted(context)) or "(none)"
            raise RenderError(f"Unknown template variable {key!r}. Available: {available}")
        return str(context[key])

    return _PLACEHOLDER.sub(_sub, template)
