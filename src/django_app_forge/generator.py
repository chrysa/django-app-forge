"""Thin shim: delegate plan()/apply() to chrysa_codegen (chrysa-lib#113, lot L2).

The engine (ActionKind, Action, plan, apply) now lives in chrysa_codegen.
This module re-exports those names for backward compatibility and provides a
django-flavoured ``plan`` wrapper that matches the pre-refactor call signature
``plan(spec, root, *, force=False)``.

No framework vocabulary (app_* / module_*) lives in the engine; each call to
chrysa_codegen.plan injects ``derived_context`` as the ``derive`` callable and
passes ``spec.apps`` as the unit collection.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from chrysa_codegen.generator import (
    Action,
    ActionKind,
    apply,
)
from chrysa_codegen.generator import plan as _codegen_plan

from .naming import derived_context
from .spec import ProjectSpec

__all__ = ["Action", "ActionKind", "apply", "plan"]


def plan(spec: ProjectSpec, root: Path, *, force: bool = False) -> list[Action]:
    """Compute the ordered list of actions to materialise *spec* under *root*.

    Delegates to ``chrysa_codegen.generator.plan``, passing ``spec.apps`` as
    the unit collection and ``derived_context`` as the per-app derive callable.
    """
    return _codegen_plan(
        spec.apps,
        spec.base_path,
        spec.context,
        root,
        derived_context,
        force=force,
    )
