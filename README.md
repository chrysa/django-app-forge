# django-app-forge

[![CI](https://github.com/chrysa/django-app-forge/actions/workflows/ci.yml/badge.svg)](https://github.com/chrysa/django-app-forge/actions/workflows/ci.yml)

Generate one or more Django apps with a **custom directory structure** from a
single YAML file. A generic, declarative replacement for the per-project Python
scaffolding scripts you copy around.

```bash
pip install django-app-forge
```

Add it to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "django_app_forge",
]
```

## Usage

```bash
python manage.py forgeapps                    # reads ./apps.yaml
python manage.py forgeapps -c apps/layout.yaml
python manage.py forgeapps --dry-run          # preview, write nothing
python manage.py forgeapps --force            # overwrite existing files
python manage.py forgeapps --base-path apps   # override the document's base_path
python manage.py forgeapps --root .           # generation root (default: cwd)
```

By default existing files are **skipped** (never clobbered); pass `--force` to
overwrite. `--dry-run` prints the full plan without touching disk.

## The YAML document

```yaml
version: 1
base_path: apps              # where apps are created, relative to --root

context:                     # extra variables for every template
  author: chrysa

templates:                   # named inline templates
  apps_py: |
    from django.apps import AppConfig


    class {{ app_class }}Config(AppConfig):
        name = "{{ app_module }}"

structures:                  # reusable, referenced by apps
  ddd:
    dirs: [migrations, tests, services]
    files:
      - path: __init__.py
        content: ""
      - path: apps.py
        template: apps_py     # reference a named template
      - path: models.py
        content: |
          from django.db import models

apps:
  - name: billing
    structure: ddd
  - name: catalog
    structure: ddd
    files:                    # per-app files extend / override the structure (by path)
      - path: services/pricing.py
        content: "# pricing for {{ app_class }}"
```

See [`apps.example.yaml`](apps.example.yaml) for a complete example, or
[`examples/demo/`](examples/demo/) for a runnable Django project you can scaffold
end to end.

### Template placeholders

Every file `path`, file `content`, and directory name is rendered with these
variables (plus anything you add under `context:`):

| Variable        | Example (`name: Api-Gateway`, `base_path: apps`) |
| --------------- | ------------------------------------------------ |
| `{{ app_name }}`   | `api_gateway` (snake_case)                    |
| `{{ app_label }}`  | `api_gateway`                                 |
| `{{ app_class }}`  | `ApiGateway` (PascalCase)                     |
| `{{ app_module }}` | `apps.api_gateway` (dotted import path)       |

A placeholder with no matching variable raises an error — generation never
emits a literal `{{ ... }}` into a file.

## Architecture

The core (`naming`, `render`, `spec`, `generator`) is **import-free of Django**
so it is unit-testable in isolation; `forgeapps` is a thin management-command
wrapper over it. `plan()` computes the actions with no side effects, `apply()`
touches the disk — which is what makes `--dry-run` exact.

## Development

```bash
make install       # editable install + pre-commit hooks
make docker-test   # full suite with coverage gate (via Docker)
make lint          # ruff
make typecheck     # mypy strict
```

Tests, lint and build run through Docker or pre-commit — never directly on the host.

## License

MIT © Anthony Gréau (chrysa)


## Documentation map

This repo follows the chrysa standardized documentation structure
(`chrysa/shared-standards/templates/docs-structure`):

- `docs/` — product, architecture, security, deployment, observability (stubs)
- `ai/`, `prompts/` — AI assets & agent prompts
- `schemas/` — JSON Schema data contracts
- `workflows/` — end-to-end flow docs
- `decisions/`, `postmortems/` — decision records & incident postmortems
- `examples/` — reference “perfect” implementations (Python)
- `tests/` — test scenario catalogues (see also the test suite)

Files marked `status: stub` are placeholders to fill in.
