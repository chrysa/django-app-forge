# TESTING — django-app-forge

> Commands below are transcribed from `Makefile` / `pyproject.toml` /
> `Dockerfile.test`. They are **not executed** in this documentation pass —
> per repo policy tests run only in Docker or pre-commit, never on the host.

## How to run (FACT)

```bash
make docker-test   # full suite with coverage gate, CI parity (Docker + BuildKit secret)
make test          # pytest (intended in-container / pre-commit context)
make test-cov      # pytest with coverage term-missing + xml
make lint          # ruff check src/django_app_forge tests
make typecheck     # mypy src/django_app_forge
make ci            # lint + typecheck + test
```

`make docker-test` builds `Dockerfile.test` passing a GitHub token as BuildKit
secret `ghtoken` (needed to fetch the private `chrysa-codegen`), then runs
`pytest --cov-report=xml`. Evidence: `Makefile`, `Dockerfile.test`.

## Configuration (FACT — `pyproject.toml`)

- `DJANGO_SETTINGS_MODULE = tests.settings`; `testpaths = ["tests"]`.
- `addopts = -v --tb=short --cov=django_app_forge --cov-report=term-missing --cov-fail-under=85`.
- Coverage source `django_app_forge`, migrations omitted.

## Suite inventory (FACT — 28 tests across 6 files)

| File | Tests | Focus |
|------|-------|-------|
| `test_spec.py` | 9 | YAML → `ProjectSpec` validation, template/structure resolution, error cases |
| `test_generator.py` | 5 | `plan`/`apply` tree creation, dry-run, skip/force, relative action describe |
| `test_command.py` | 5 | `forgeapps` command: generation, dry-run, base-path override, missing/invalid config errors |
| `test_naming.py` | 4 | `to_snake`, `to_pascal`, `derived_context` (with/without base_path) |
| `test_render.py` | 4 | placeholder substitution, whitespace tolerance, identity, unknown-var raise |
| `test_golden.py` | 1 | AC-L2-05 byte-identical output vs `tests/golden/django/default/` |

Named tests: `test_load_valid_spec`, `test_template_reference_resolved`,
`test_per_app_file_overrides_structure_by_path`, `test_missing_apps_raises`,
`test_unsupported_version_raises`, `test_unknown_structure_raises`,
`test_unknown_template_raises`, `test_file_needs_exactly_one_source`,
`test_file_requires_path`; `test_plan_and_apply_creates_tree`,
`test_dry_run_writes_nothing`, `test_existing_file_is_skipped_without_force`,
`test_force_overwrites`, `test_action_describe_is_relative`;
`test_command_generates_apps`, `test_command_dry_run_writes_nothing`,
`test_command_base_path_override`, `test_command_missing_config_errors`,
`test_command_invalid_spec_errors`; `test_to_snake`, `test_to_pascal`,
`test_derived_context_with_base_path`, `test_derived_context_root_base_path`;
`test_render_replaces_placeholders`, `test_render_tolerates_whitespace`,
`test_render_no_placeholder_is_identity`, `test_render_unknown_variable_raises`;
`test_golden_output_is_byte_identical`.

## Golden fixture (FACT)

`tests/golden/django/default/` holds `input.yaml` (the canonical
`apps.example.yaml`) and `sha256map.json` (`{relpath: sha256}`). Any deviation
in generated output fails the gate. Evidence: `test_golden.py` docstring.

## Test scenario catalogues (stubs)

`tests/e2e-scenarios.md`, `tests/edge-cases.md`, `tests/regression-tests.md`
exist but are `status: stub` placeholders (docs-structure boilerplate), not
populated scenario catalogues. **UNKNOWN** intended contents.
