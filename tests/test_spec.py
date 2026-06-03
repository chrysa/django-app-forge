import pytest

from django_app_forge.spec import SpecError, load_spec

VALID = {
    "version": 1,
    "base_path": "apps",
    "context": {"author": "chrysa"},
    "templates": {"apps_py": "name = {{ app_module }}"},
    "structures": {
        "ddd": {
            "dirs": ["migrations", "tests"],
            "files": [
                {"path": "__init__.py", "content": ""},
                {"path": "apps.py", "template": "apps_py"},
            ],
        }
    },
    "apps": [
        {"name": "billing", "structure": "ddd"},
        {
            "name": "catalog",
            "structure": "ddd",
            "dirs": ["services"],
            "files": [{"path": "services.py", "content": "x"}],
        },
    ],
}


def test_load_valid_spec() -> None:
    spec = load_spec(VALID)
    assert spec.base_path == "apps"
    assert spec.context == {"author": "chrysa"}
    assert [a.name for a in spec.apps] == ["billing", "catalog"]

    catalog = spec.apps[1]
    assert "services" in catalog.dirs
    assert {f.path for f in catalog.files} == {"__init__.py", "apps.py", "services.py"}


def test_template_reference_resolved() -> None:
    spec = load_spec(VALID)
    apps_file = next(f for f in spec.apps[0].files if f.path == "apps.py")
    assert apps_file.content == "name = {{ app_module }}"


def test_per_app_file_overrides_structure_by_path() -> None:
    data = {
        "apps": [
            {
                "name": "x",
                "structure": "s",
                "files": [{"path": "models.py", "content": "override"}],
            }
        ],
        "structures": {"s": {"files": [{"path": "models.py", "content": "base"}]}},
    }
    spec = load_spec(data)
    models = next(f for f in spec.apps[0].files if f.path == "models.py")
    assert models.content == "override"


def test_missing_apps_raises() -> None:
    with pytest.raises(SpecError, match="non-empty list"):
        load_spec({"version": 1})


def test_unsupported_version_raises() -> None:
    with pytest.raises(SpecError, match="Unsupported version"):
        load_spec({"version": 2, "apps": [{"name": "x"}]})


def test_unknown_structure_raises() -> None:
    with pytest.raises(SpecError, match="unknown structure"):
        load_spec({"apps": [{"name": "x", "structure": "nope"}]})


def test_unknown_template_raises() -> None:
    with pytest.raises(SpecError, match="unknown template"):
        load_spec({"apps": [{"name": "x", "files": [{"path": "a.py", "template": "nope"}]}]})


def test_file_needs_exactly_one_source() -> None:
    with pytest.raises(SpecError, match="exactly one"):
        load_spec({"apps": [{"name": "x", "files": [{"path": "a.py", "content": "c", "template": "t"}]}]})


def test_file_requires_path() -> None:
    with pytest.raises(SpecError, match="requires a non-empty string 'path'"):
        load_spec({"apps": [{"name": "x", "files": [{"content": "c"}]}]})
