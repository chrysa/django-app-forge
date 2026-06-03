from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

CONFIG = """
version: 1
base_path: apps
templates:
  apps_py: |
    class {{ app_class }}Config:
        name = "{{ app_module }}"
structures:
  ddd:
    dirs: [migrations]
    files:
      - path: __init__.py
        content: ""
      - path: apps.py
        template: apps_py
apps:
  - name: billing
    structure: ddd
"""


def _write_config(tmp_path: Path) -> Path:
    config = tmp_path / "apps.yaml"
    config.write_text(CONFIG)
    return config


def test_command_generates_apps(tmp_path: Path) -> None:
    config = _write_config(tmp_path)
    call_command("forgeapps", config=str(config), root=str(tmp_path))

    apps_py = tmp_path / "apps" / "billing" / "apps.py"
    assert apps_py.is_file()
    assert 'name = "apps.billing"' in apps_py.read_text()


def test_command_dry_run_writes_nothing(tmp_path: Path) -> None:
    config = _write_config(tmp_path)
    call_command("forgeapps", config=str(config), root=str(tmp_path), dry_run=True)
    assert not (tmp_path / "apps").exists()


def test_command_base_path_override(tmp_path: Path) -> None:
    config = _write_config(tmp_path)
    call_command("forgeapps", config=str(config), root=str(tmp_path), base_path="services")
    assert (tmp_path / "services" / "billing" / "apps.py").is_file()


def test_command_missing_config_errors(tmp_path: Path) -> None:
    with pytest.raises(CommandError, match="Config file not found"):
        call_command("forgeapps", config=str(tmp_path / "nope.yaml"))


def test_command_invalid_spec_errors(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("version: 1\napps: []\n")
    with pytest.raises(CommandError, match="Invalid forge document"):
        call_command("forgeapps", config=str(bad), root=str(tmp_path))
