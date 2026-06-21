"""Re-export render primitives from chrysa_codegen.

The local implementation has been removed in favour of the shared
``chrysa-codegen`` package (chrysa-lib#113, lot L2). This shim preserves
the existing public import path ``django_app_forge.render`` for any caller
that imports directly from this module.
"""

from __future__ import annotations

from chrysa_codegen.render import RenderError, render

__all__ = ["RenderError", "render"]
