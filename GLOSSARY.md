# GLOSSARY — django-app-forge

> Terms as used in this repo. Evidence = repo-relative paths.

| Term | Meaning |
|------|---------|
| **forge document** | The YAML file (default `apps.yaml`) describing `version`, `base_path`, `context`, `templates`, `structures`, `apps`. Evidence: `README.md`, `apps.example.yaml`. |
| **`forgeapps`** | The Django management command that reads a forge document and generates apps. Evidence: `management/commands/forgeapps.py`. |
| **structure** | A named, reusable set of `dirs` + `files` an app references. Evidence: `spec.py`, `apps.example.yaml`. |
| **template** | A named inline text template referenced by a file entry via `template:`. Evidence: `spec.py`. |
| **app** | An entry under `apps:` — a Django app to generate; references a `structure` and may extend/override files by path. Evidence: `spec.py`. |
| **`ProjectSpec` / `AppSpec` / `FileSpec`** | Typed dataclasses produced by validating the forge document. Evidence: `spec.py`. |
| **derived context** | Per-app template variables merged with global `context`. Evidence: `naming.derived_context`. |
| **`app_name`** | snake_case app name (e.g. `api_gateway`). Evidence: `README.md`, `naming.py`. |
| **`app_label`** | The app's label (same snake form). Evidence: `README.md`. |
| **`app_class`** | PascalCase name (e.g. `ApiGateway`). Evidence: `README.md`. |
| **`app_module`** | Dotted Python import path (e.g. `apps.api_gateway`), derived from `base_path`. Evidence: `naming.py`. |
| **`base_path`** | Directory (relative to `--root`) apps are created under; drives `app_module`. Evidence: `README.md`, `naming.py`. |
| **`plan()`** | Pure function computing the ordered list of `Action`s (no disk writes). Evidence: `generator.py`. |
| **`apply()`** | Executes the plan against disk; `dry_run=True` writes nothing. Evidence: `generator.py`. |
| **`Action` / `ActionKind`** | An intended operation; kinds `MKDIR`, `WRITE`, `SKIP`. Evidence: `forgeapps.py`. |
| **`SpecError` / `RenderError`** | Typed errors: `SpecError` (structural problems, defined in `spec.py`) and `RenderError` (unknown placeholder, from the `chrysa-codegen` render layer). Both surface via the command as `CommandError`. Evidence: `spec.py`, `render.py`, `test_render_unknown_variable_raises`. |
| **golden fixture / AC-L2-05** | `tests/golden/django/default/`: the `{relpath: sha256}` map that locks byte-identical output. Evidence: `test_golden.py`. |
| **chrysa-codegen** | The shared generation engine (private `chrysa/chrysa-lib` monorepo) re-exported here; owns `plan`/`apply`/`render`. Evidence: `README.md`, `pyproject.toml`. |
| **`--force`** | Overwrite existing files instead of skipping them. Evidence: `forgeapps.py`. |
| **`--dry-run`** | Print the plan, write nothing. Evidence: `forgeapps.py`. |
