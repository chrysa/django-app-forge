"""Name-derivation helpers (no Django, no third-party deps).

``to_snake`` and ``to_pascal`` are delegated to ``chrysa_codegen.naming``
(chrysa-lib#113, lot L2). ``derived_context`` is django-specific and stays
local: it builds the ``app_*`` template variables that each forge owns.
"""

from __future__ import annotations

import re

from chrysa_codegen.naming import to_pascal, to_snake

__all__ = ["derived_context", "to_pascal", "to_snake"]


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
