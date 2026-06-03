from pathlib import Path

from django_app_forge.generator import ActionKind, apply, plan
from django_app_forge.spec import load_spec

DOC = {
    "base_path": "apps",
    "templates": {"apps_py": "name = {{ app_module }}\nclass {{ app_class }}Config: ..."},
    "structures": {
        "ddd": {
            "dirs": ["migrations"],
            "files": [
                {"path": "__init__.py", "content": ""},
                {"path": "apps.py", "template": "apps_py"},
            ],
        }
    },
    "apps": [{"name": "Billing", "structure": "ddd"}],
}


def test_plan_and_apply_creates_tree(tmp_path: Path) -> None:
    spec = load_spec(DOC)
    actions = plan(spec, tmp_path)
    apply(actions)

    app_dir = tmp_path / "apps" / "billing"
    assert (app_dir / "migrations").is_dir()
    assert (app_dir / "__init__.py").is_file()

    apps_py = (app_dir / "apps.py").read_text()
    assert "name = apps.billing" in apps_py
    assert "class BillingConfig" in apps_py


def test_dry_run_writes_nothing(tmp_path: Path) -> None:
    spec = load_spec(DOC)
    performed = apply(plan(spec, tmp_path), dry_run=True)
    assert performed  # actions were reported
    assert not (tmp_path / "apps").exists()


def test_existing_file_is_skipped_without_force(tmp_path: Path) -> None:
    spec = load_spec(DOC)
    apply(plan(spec, tmp_path))
    target = tmp_path / "apps" / "billing" / "apps.py"
    target.write_text("HAND EDITED")

    actions = plan(spec, tmp_path)
    assert any(a.kind is ActionKind.SKIP and a.path == target for a in actions)
    apply(actions)
    assert target.read_text() == "HAND EDITED"


def test_force_overwrites(tmp_path: Path) -> None:
    spec = load_spec(DOC)
    apply(plan(spec, tmp_path))
    target = tmp_path / "apps" / "billing" / "apps.py"
    target.write_text("HAND EDITED")

    apply(plan(spec, tmp_path, force=True))
    assert "name = apps.billing" in target.read_text()


def test_action_describe_is_relative(tmp_path: Path) -> None:
    spec = load_spec(DOC)
    actions = plan(spec, tmp_path)
    descriptions = [a.describe(tmp_path) for a in actions]
    assert any("apps/billing/apps.py" in d for d in descriptions)
