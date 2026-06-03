# django-app-forge — GitHub Copilot Instructions

## Purpose

Generate Django apps with a custom directory structure from a YAML file. A
generic, declarative replacement for per-project Python scaffolding scripts.

## Conventions

- Python ≥3.14, Django ≥4.2. Flat layout (`django_app_forge/`, `tests/`).
- Deps: Django, PyYAML. The core (naming/render/spec/generator) MUST stay
  import-free of Django so it is unit-testable in isolation.
- `forgeapps` management command is a thin wrapper over the core.
- ruff (line 120), mypy strict (django-stubs), coverage `fail_under = 85`.
- All tests/lint/build go through Docker or pre-commit — never on host.

## Commands

`make docker-test` · `make lint` · `make typecheck` · `make test-cov`
