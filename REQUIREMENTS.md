# REQUIREMENTS — django-app-forge

> Consolidated traceability matrix. **IMPLEMENTED** is asserted only where a
> code path AND a test (or explicit config) verify it. Detailed requirements
> live in [`PRD.md`](PRD.md) and [`TRD.md`](TRD.md).

## Product requirements

| ID | Requirement | Status | Evidence |
|----|-------------|--------|----------|
| REQ-PROD-001 | Generate ≥1 Django app from one YAML document | IMPLEMENTED | `forgeapps.py`, `test_command_generates_apps` |
| REQ-PROD-002 | Reusable named `structures` | IMPLEMENTED | `spec.py`, `test_load_valid_spec` |
| REQ-PROD-003 | Named inline `templates` | IMPLEMENTED | `spec.py`, `test_template_reference_resolved` |
| REQ-PROD-004 | Per-app files extend/override structure by path | IMPLEMENTED | `spec.py`, `test_per_app_file_overrides_structure_by_path` |
| REQ-PROD-005 | Placeholder rendering in paths/contents/dir names | IMPLEMENTED | `naming.py`, `render.py`, `test_render_*` |
| REQ-PROD-006 | Unknown placeholder raises | IMPLEMENTED | `render.py`, `test_render_unknown_variable_raises` |
| REQ-PROD-007 | Skip existing by default; `--force` overwrites | IMPLEMENTED | `forgeapps.py`, `test_existing_file_is_skipped_without_force`, `test_force_overwrites` |
| REQ-PROD-008 | `--dry-run` writes nothing | IMPLEMENTED | `test_command_dry_run_writes_nothing`, `test_dry_run_writes_nothing` |
| REQ-PROD-009 | `-c` / `--root` / `--base-path` overrides | IMPLEMENTED | `forgeapps.py`, `test_command_base_path_override` |
| REQ-PROD-010 | Actionable errors (missing config / bad YAML / bad spec) | IMPLEMENTED | `forgeapps.py`, `test_command_missing_config_errors`, `test_command_invalid_spec_errors` |

## Technical requirements

| ID | Requirement | Status | Evidence |
|----|-------------|--------|----------|
| REQ-TECH-001 | Core import-free of Django | IMPLEMENTED | `CLAUDE.md`, modules, core tests |
| REQ-TECH-002 | `plan()` pure / `apply()` writes | IMPLEMENTED | `generator.py`, `test_dry_run_writes_nothing` |
| REQ-TECH-003 | `version: 1` enforced | IMPLEMENTED | `test_unsupported_version_raises` |
| REQ-TECH-004 | file = path + exactly one of content/template | IMPLEMENTED | `test_file_needs_exactly_one_source`, `test_file_requires_path` |
| REQ-TECH-005 | Unknown structure/template rejected | IMPLEMENTED | `test_unknown_structure_raises`, `test_unknown_template_raises` |
| REQ-TECH-006 | Non-empty `apps` required | IMPLEMENTED | `test_missing_apps_raises` |
| REQ-TECH-007 | Dotted `app_module` from base_path | IMPLEMENTED | `test_derived_context_with_base_path`, `test_derived_context_root_base_path` |
| REQ-TECH-008 | Byte-identical golden output | IMPLEMENTED | `test_golden_output_is_byte_identical` (AC-L2-05) |
| REQ-TECH-009 | Coverage ≥ 85% | IMPLEMENTED | `pyproject.toml` `--cov-fail-under=85` |
| REQ-TECH-010 | Typed library, mypy strict | IMPLEMENTED | `py.typed`, `pyproject.toml` |
| REQ-TECH-011 | No host test/lint/build | IMPLEMENTED | `Makefile`, `Dockerfile.test`, hookify rule |

## Notes

- **UNKNOWN** No formal external spec/PRD document is stored in the repo; these
  requirements are reconstructed from code, tests, and README/CLAUDE/AGENTS.
- The `docs/`, `decisions/`, `schemas/`, `workflows/`, `prompts/`, `postmortems/`,
  `legal/` trees currently hold **generic docs-structure boilerplate stubs**
  (auth-provider, payment, sales-agent, etc.) that do not describe this
  scaffolder — see [`REVIEW.md`](REVIEW.md).
