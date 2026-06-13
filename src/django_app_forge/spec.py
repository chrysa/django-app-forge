"""Parse and validate a forge YAML document into typed specs.

No Django import here: this module turns raw data (already loaded from YAML)
into validated dataclasses, resolving named ``structures`` and ``templates``
references. Placeholders inside file contents/paths are left untouched — they
are rendered later, per app, by :mod:`django_app_forge.generator`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

SUPPORTED_VERSION = 1


class SpecError(ValueError):
    """Raised on any structural problem in the forge document."""


@dataclass(frozen=True)
class FileSpec:
    path: str
    content: str


@dataclass(frozen=True)
class AppSpec:
    name: str
    dirs: tuple[str, ...]
    files: tuple[FileSpec, ...]


@dataclass(frozen=True)
class ProjectSpec:
    version: int
    base_path: str
    context: dict[str, str]
    apps: tuple[AppSpec, ...]


def _require_mapping(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SpecError(f"{where} must be a mapping, got {type(value).__name__}")
    return value


def _resolve_files(
    raw_files: Any,
    templates: dict[str, str],
    where: str,
) -> dict[str, FileSpec]:
    """Resolve a list of file entries into a {path: FileSpec} map.

    Each entry needs a ``path`` and exactly one of ``content`` / ``template``
    (a ``template`` references a named entry in the top-level ``templates``).
    """
    if raw_files is None:
        return {}
    if not isinstance(raw_files, list):
        raise SpecError(f"{where}.files must be a list")

    out: dict[str, FileSpec] = {}
    for index, entry in enumerate(raw_files):
        loc = f"{where}.files[{index}]"
        entry = _require_mapping(entry, loc)
        path = entry.get("path")
        if not path or not isinstance(path, str):
            raise SpecError(f"{loc} requires a non-empty string 'path'")
        has_content = "content" in entry
        has_template = "template" in entry
        if has_content == has_template:
            raise SpecError(f"{loc} needs exactly one of 'content' or 'template'")
        if has_template:
            tpl = entry["template"]
            if tpl not in templates:
                raise SpecError(f"{loc} references unknown template {tpl!r}")
            content = templates[tpl]
        else:
            content = entry["content"]
            if content is None:
                content = ""
            if not isinstance(content, str):
                raise SpecError(f"{loc}.content must be a string")
        out[path] = FileSpec(path=path, content=content)
    return out


def _resolve_dirs(raw_dirs: Any, where: str) -> list[str]:
    if raw_dirs is None:
        return []
    if not isinstance(raw_dirs, list) or not all(isinstance(d, str) for d in raw_dirs):
        raise SpecError(f"{where}.dirs must be a list of strings")
    return list(raw_dirs)


def load_spec(data: Any) -> ProjectSpec:
    """Validate a raw forge document and return a :class:`ProjectSpec`."""
    data = _require_mapping(data, "document root")

    version = data.get("version", SUPPORTED_VERSION)
    if version != SUPPORTED_VERSION:
        raise SpecError(f"Unsupported version {version!r}; expected {SUPPORTED_VERSION}")

    base_path = data.get("base_path", ".")
    if not isinstance(base_path, str):
        raise SpecError("base_path must be a string")

    global_context = data.get("context", {})
    global_context = _require_mapping(global_context, "context")
    context = {str(k): str(v) for k, v in global_context.items()}

    templates_raw = _require_mapping(data.get("templates", {}), "templates")
    templates: dict[str, str] = {}
    for name, body in templates_raw.items():
        if not isinstance(body, str):
            raise SpecError(f"templates.{name} must be a string")
        templates[str(name)] = body

    structures_raw = _require_mapping(data.get("structures", {}), "structures")
    structures: dict[str, tuple[list[str], dict[str, FileSpec]]] = {}
    for name, body in structures_raw.items():
        body = _require_mapping(body, f"structures.{name}")
        structures[str(name)] = (
            _resolve_dirs(body.get("dirs"), f"structures.{name}"),
            _resolve_files(body.get("files"), templates, f"structures.{name}"),
        )

    apps_raw = data.get("apps")
    if not isinstance(apps_raw, list) or not apps_raw:
        raise SpecError("'apps' must be a non-empty list")

    apps: list[AppSpec] = []
    for index, entry in enumerate(apps_raw):
        loc = f"apps[{index}]"
        entry = _require_mapping(entry, loc)
        app_name = entry.get("name")
        if not app_name or not isinstance(app_name, str):
            raise SpecError(f"{loc} requires a non-empty string 'name'")

        dirs: list[str] = []
        files: dict[str, FileSpec] = {}

        structure = entry.get("structure")
        if structure is not None:
            if structure not in structures:
                raise SpecError(f"{loc} references unknown structure {structure!r}")
            base_dirs, base_files = structures[structure]
            dirs = list(base_dirs)
            files = dict(base_files)

        # Per-app dirs/files extend (and override by path) the structure.
        for extra_dir in _resolve_dirs(entry.get("dirs"), loc):
            if extra_dir not in dirs:
                dirs.append(extra_dir)
        files.update(_resolve_files(entry.get("files"), templates, loc))

        apps.append(
            AppSpec(
                name=app_name,
                dirs=tuple(dirs),
                files=tuple(files.values()),
            )
        )

    return ProjectSpec(
        version=version,
        base_path=base_path,
        context=context,
        apps=tuple(apps),
    )
