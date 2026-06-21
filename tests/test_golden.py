"""AC-L2-05 golden-file gate: byte-identical output pre/post chrysa-codegen swap.

Fixture ``tests/golden/django/default/`` was captured from origin/main (pre-swap)
by running the full django-app-forge generation pipeline against ``apps.example.yaml``
and hashing every generated file as ``{relpath: sha256(content)}``.

After the swap (this branch) the same pipeline must produce an identical map.
Any deviation is a regression, not a warning.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
import yaml

from django_app_forge.generator import apply, plan
from django_app_forge.spec import load_spec

GOLDEN_DIR = Path(__file__).parent / "golden" / "django" / "default"


def _sha256map(root: Path) -> dict[str, str]:
    """Return ``{relpath: sha256hex}`` for every file under *root*."""
    return {
        str(f.relative_to(root)): hashlib.sha256(f.read_bytes()).hexdigest()
        for f in sorted(root.rglob("*"))
        if f.is_file()
    }


def test_golden_output_is_byte_identical(tmp_path: Path) -> None:
    """Post-swap output must be byte-identical to the pre-swap golden fixture.

    AC-L2-05: for the canonical ``apps.example.yaml`` input, the
    ``{relpath: sha256(content)}`` map produced by the post-swap pipeline must
    match the committed golden map exactly — no additions, no omissions, no
    content drift.
    """
    expected: dict[str, str] = json.loads((GOLDEN_DIR / "sha256map.json").read_text())

    raw = yaml.safe_load((GOLDEN_DIR / "input.yaml").read_text(encoding="utf-8"))
    spec = load_spec(raw)
    actions = plan(spec, tmp_path)
    apply(actions)

    actual = _sha256map(tmp_path)

    missing = set(expected) - set(actual)
    extra = set(actual) - set(expected)
    drifted = {k for k in expected if k in actual and expected[k] != actual[k]}

    assert not missing, f"Missing generated files: {sorted(missing)}"
    assert not extra, f"Unexpected extra files: {sorted(extra)}"
    assert not drifted, (
        f"Content drift detected in: {sorted(drifted)}\n"
        + "\n".join(f"  {k}: expected={expected[k]} actual={actual[k]}" for k in sorted(drifted))
    )
