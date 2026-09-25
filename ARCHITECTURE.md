# ARCHITECTURE — django-app-forge

> Tags: **FACT** / **INFERENCE** / **UNKNOWN**. Evidence = repo-relative paths.

## One-liner

**FACT** A thin Django adapter over the shared `chrysa-codegen` generation
engine. The core stays import-free of Django so it is unit-testable in isolation.
(Evidence: `README.md` "Architecture", `CLAUDE.md`, `AGENTS.md`.)

## Components (`src/django_app_forge/`)

| Module | Role | Django-free? | Evidence |
|--------|------|--------------|----------|
| `spec.py` | Parse + validate the YAML document into typed dataclasses (`ProjectSpec`, `AppSpec`, `FileSpec`); raises `SpecError` | yes | `spec.py`, `test_spec.py` |
| `naming.py` | `to_snake`/`to_pascal` (re-exported from engine) + `derived_context` building the per-app `app_name/app_label/app_class/app_module` variables | yes | `naming.py`, `test_naming.py` |
| `render.py` | `{{ var }}` substitution; fails loud on unknown variables (`RenderError`) | yes | `render.py`, `test_render.py` |
| `generator.py` | `plan()` (pure, computes ordered `Action`s) → `apply()` (touches disk) | yes | `generator.py`, `test_generator.py` |
| `apps.py` | `AppConfig` (`verbose_name = "Django App Forge"`) | no (Django) | `apps.py` |
| `management/commands/forgeapps.py` | Thin `manage.py` wrapper: arg parsing, load YAML, call spec/plan/apply, report | no (Django) | `forgeapps.py`, `test_command.py` |

**FACT** `generator`, `render`, and `naming.to_snake/to_pascal` are re-exported
from `chrysa_codegen`; the engine (`plan`/`apply`/`render`) lives there, not
here. (Evidence: `README.md` "Architecture".)

## Data flow

**FACT / INFERENCE** (from `forgeapps.handle` and module roles):

```
apps.yaml ──yaml.safe_load──▶ dict
   └─ spec.load_spec(dict) ─▶ ProjectSpec (validated, typed)
        └─ generator.plan(spec, root, force) ─▶ [Action(kind=MKDIR|WRITE|SKIP, …)]  (no side effects)
             └─ generator.apply(actions, dry_run) ─▶ disk writes (skipped when dry_run)
                  └─ command prints "Generated/Would generate N app(s): D dir(s), F file(s), S skipped."
```

Per app, `derived_context` merges the global `context` with the derived
`app_*` names; `render` substitutes those into every file path, file content,
and directory name. **FACT** A placeholder with no matching variable raises.

## Key properties

- **FACT** `plan()` has no side effects; `apply(dry_run=True)` reports actions
  but writes nothing — this is what makes `--dry-run` exact
  (`test_dry_run_writes_nothing`).
- **FACT** Existing files are `SKIP` by default; `--force` switches to overwrite.
- **FACT** `ActionKind` enum = `MKDIR` / `WRITE` / `SKIP`. (Evidence: `forgeapps.py`.)

## Boundaries & dependencies

- **FACT** Runtime deps: Django (≥4.2), PyYAML, and `chrysa-codegen`
  (git-pinned, private). (Evidence: `pyproject.toml`, `README.md`.)
- **FACT** `chrysa-codegen` is a package of the private `chrysa/chrysa-lib`
  monorepo, pinned by commit SHA in `pyproject.toml`
  (`…@10b75e14…#subdirectory=packages/python/codegen`). Installation requires a
  GitHub token with read access to `chrysa/chrysa-lib`.
- **INFERENCE** Relationship to `project-init`: `context-map.json` and the
  chrysa standards ("every code repo depends on `project-init`") indicate this
  repo was bootstrapped from the chrysa `project-init` scaffold, but no direct
  code dependency on `project-init` is present. **UNKNOWN** beyond that.

## Packaging

**FACT** `src/` layout, distributed as the `django-app-forge` package; ships
`py.typed` (typed library). (Evidence: `pyproject.toml`, `src/.../py.typed`.)
