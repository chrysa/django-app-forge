# Architecture — django-app-forge

> Grounded in the repository's manifests and source. Where documentation and
> manifests disagree, the manifests win.

## Purpose

Generate one or more Django apps with a custom directory structure from a single
YAML file. A generic, declarative replacement for the per-project Python
scaffolding scripts otherwise copied around. Existing files are skipped by
default (never clobbered); `--force` overwrites and `--dry-run` previews without
touching disk.

## Stack

- **Language:** Python `>=3.14` (packaging target; note ruff config comments that
  the toolchain currently pins some behaviour to py313 due to an upstream bug).
- **Framework:** Django `>=4.2` (integrates as a Django app exposing a management
  command).
- **Runtime deps:** `PyYAML>=6.0`; `chrysa-codegen` — the generation engine —
  pulled from the **private** `chrysa/chrysa-lib` monorepo via a pinned git URL
  (`packages/python/codegen`). Installation therefore requires GitHub read
  credentials; in CI the token is passed as a BuildKit secret (`ghtoken`).
- **Build backend:** setuptools (`pyproject.toml`, src layout).
- **Tooling:** pytest + pytest-django + pytest-cov, ruff (lint + format), mypy
  (strict) with django-stubs.

## Layout

```
src/django_app_forge/
├── naming.py        # snake/Pascal + per-app derived context (no Django)
├── render.py        # {{ var }} substitution, fails loud on unknown vars (no Django)
├── spec.py          # parse + validate YAML into dataclasses (no Django)
├── generator.py     # plan() pure → apply() touches disk (no Django)
├── apps.py          # Django AppConfig
├── py.typed         # typing marker
└── management/commands/forgeapps.py  # thin Django wrapper over the core
tests/               # pytest suites (spec, render, naming, generator, command, golden)
examples/demo/       # runnable Django project to scaffold against
apps.example.yaml    # complete example spec
scripts/             # gen_context_files.py, quality_gate.py (repo tooling)
docs/                # extended docs (architecture.md, security.md, deployment.md, …)
```

The core modules (`naming`, `render`, `spec`, `generator`) are Django-free and
pure; `plan()` is pure and `apply()` is the only disk-touching step. The Django
management command is a thin wrapper over that core.

## Entrypoints

- **`python manage.py forgeapps`** — the Django management command
  (`src/django_app_forge/management/commands/forgeapps.py`). Flags include
  `--dry-run` (preview, write nothing) and `--force` (overwrite existing files).
- Installed/registered as a Django app via `apps.py` (AppConfig).

## Data / External deps

- **Input:** a YAML spec file (see `apps.example.yaml`) describing apps, a
  directory `structure`, and per-app `files` that extend/override by path. File
  paths, contents, and directory names are rendered with `{{ var }}`
  substitution; an unmatched placeholder raises an error (generation never
  produces a half-templated file).
- **External services:** private git dependency `chrysa-codegen` from
  `chrysa/chrysa-lib` (GitHub, credentialed). No database or network runtime
  dependency of its own beyond Django.
- **Output:** generated app files written to disk (skipped if present unless
  `--force`); files marked `status: stub` are placeholders to fill in.

## Build & test

Real commands (from `Makefile` / `pyproject.toml`):

```bash
make install      # pip install -e ".[dev]" + pre-commit install
make test         # pytest
make test-cov     # pytest with coverage (fail-under 85%)
make lint         # ruff check src/django_app_forge tests
make format       # ruff format + ruff check --fix
make typecheck    # mypy src/django_app_forge
make ci           # lint + typecheck + test
make docker-test  # CI-parity run in Docker (Dockerfile.test, ghtoken BuildKit secret)
make build        # python -m build (wheel)
```

pytest is configured with `pythonpath = [".", "src"]`, `testpaths = ["tests"]`,
Django settings at `tests/settings.py`, and `--cov-fail-under=85`.
