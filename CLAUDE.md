# CLAUDE.md — django-app-forge

Generate Django apps with a custom structure from a YAML file. A generic,
declarative replacement for per-project Python scaffolding scripts.

## Layout

```
django_app_forge/
├── naming.py       # snake/Pascal + per-app derived context (no Django)
├── render.py       # {{ var }} substitution, fails loud on unknown vars (no Django)
├── spec.py         # parse + validate YAML doc into dataclasses (no Django)
├── generator.py    # plan() pure → apply() touches disk (no Django)
├── apps.py         # AppConfig
└── management/commands/forgeapps.py  # thin Django wrapper over the core
tests/              # test_*.py — core unit tests + command integration
apps.example.yaml   # reference document
```

## Conventions

- Python ≥3.14, Django ≥4.2. Flat layout. Deps: Django, PyYAML.
- The core (naming/render/spec/generator) MUST stay import-free of Django.
- ruff (line 120), mypy strict (django-stubs), coverage `fail_under = 85`.
- All tests/lint/build go through Docker or pre-commit — never on host.

## Commands (always `make <target>`)

`make docker-test` · `make lint` · `make typecheck` · `make test-cov`

## Design notes

- `plan()` has no side effects; `apply(dry_run=True)` reports actions but writes
  nothing — `--dry-run` is therefore exact.
- Existing files are SKIP by default; `--force` to overwrite. Never clobber by default.
- Placeholders are resolved per app (global `context` + derived names), in file
  paths, file contents, and directory names.

<!-- chrysa:standards-import:start -->
@.chrysa/STANDARDS.md
<!-- chrysa:standards-import:end -->
