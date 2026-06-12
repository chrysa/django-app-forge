"""Turn a :class:`ProjectSpec` into filesystem actions (no Django import).

The generator is split into a pure :func:`plan` step (compute the actions, no
side effects) and an :func:`apply` step (touch the disk). This keeps ``--dry-run``
trivial and the whole thing unit-testable against a ``tmp_path``.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from .naming import derived_context
from .render import render
from .spec import AppSpec, ProjectSpec


class ActionKind(StrEnum):
    MKDIR = "mkdir"
    WRITE = "write"
    SKIP = "skip"  # file already exists and force is off


@dataclass(frozen=True)
class Action:
    kind: ActionKind
    path: Path
    content: str = ""

    def describe(self, root: Path) -> str:
        try:
            rel = self.path.relative_to(root)
        except ValueError:
            rel = self.path
        return f"{self.kind.value:5} {rel}"


def _app_context(spec: ProjectSpec, app: AppSpec) -> dict[str, str]:
    ctx = dict(spec.context)
    ctx.update(derived_context(app.name, spec.base_path))
    return ctx


def plan(spec: ProjectSpec, root: Path, *, force: bool = False) -> list[Action]:
    """Compute the ordered list of actions to materialize *spec* under *root*.

    Existing files become ``SKIP`` unless *force* is set. Directory paths and
    file paths/contents are rendered with the per-app context, so placeholders
    work everywhere.
    """
    root = Path(root)
    actions: list[Action] = []
    seen_dirs: set[Path] = set()

    def ensure_dir(path: Path) -> None:
        if path in seen_dirs:
            return
        seen_dirs.add(path)
        if not path.exists():
            actions.append(Action(ActionKind.MKDIR, path))

    for app in spec.apps:
        ctx = _app_context(spec, app)
        app_dirname = render(app.name, ctx) if "{{" in app.name else ctx["app_name"]
        app_root = root / render(spec.base_path, ctx) / app_dirname

        ensure_dir(app_root)
        for raw_dir in app.dirs:
            ensure_dir(app_root / render(raw_dir, ctx))

        for file_spec in app.files:
            target = app_root / render(file_spec.path, ctx)
            ensure_dir(target.parent)
            if target.exists() and not force:
                actions.append(Action(ActionKind.SKIP, target))
                continue
            actions.append(Action(ActionKind.WRITE, target, render(file_spec.content, ctx)))

    return actions


def apply(actions: Iterable[Action], *, dry_run: bool = False) -> list[Action]:
    """Execute *actions* (unless *dry_run*). Returns the actions actually run."""
    performed: list[Action] = []
    for action in actions:
        if action.kind is ActionKind.SKIP:
            continue
        if not dry_run:
            if action.kind is ActionKind.MKDIR:
                action.path.mkdir(parents=True, exist_ok=True)
            elif action.kind is ActionKind.WRITE:
                action.path.parent.mkdir(parents=True, exist_ok=True)
                action.path.write_text(action.content, encoding="utf-8")
        performed.append(action)
    return performed
