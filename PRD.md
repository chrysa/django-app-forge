# PRD — django-app-forge

> Product Requirements. Tags: **FACT** (verifiable in-repo), **INFERENCE** (reasoned),
> **UNKNOWN** (not determinable from the repo), **PROPOSAL** (suggested, not decided).
> Evidence pointers are repo-relative paths.

## Problem

**FACT** Django's `startapp` produces a fixed, flat app layout. Teams that want a
custom per-app directory structure (e.g. DDD-style `services/`, `tests/`,
`migrations/`) copy per-project Python scaffolding scripts around.
(Evidence: `README.md`, `AGENTS.md` "What this is".)

## Product

**FACT** `django-app-forge` generates one or more Django apps with a custom
directory structure from a single declarative YAML document, exposed as the
`manage.py forgeapps` management command. It is a generic, declarative
replacement for those per-project scaffolding scripts.
(Evidence: `README.md`, `src/django_app_forge/management/commands/forgeapps.py`.)

## Users

**INFERENCE** Django developers / platform teams inside the chrysa ecosystem who
create apps with a non-default structure. **UNKNOWN** external adoption metrics.

## Value proposition

- **FACT** One YAML document describes reusable `structures`, named `templates`,
  and a list of `apps`; apps reference a structure and may extend/override it.
- **FACT** Safe by default: existing files are **skipped**, never clobbered;
  `--force` opts into overwrite. (Evidence: `forgeapps.py`, README "Usage".)
- **FACT** `--dry-run` prints the exact plan and writes nothing — exactness is
  test-asserted. (Evidence: `test_command_dry_run_writes_nothing`,
  `test_dry_run_writes_nothing`.)

## Product requirements

| ID | Requirement | Status | Evidence |
|----|-------------|--------|----------|
| REQ-PROD-001 | Generate ≥1 Django app from a single YAML document | IMPLEMENTED | `forgeapps.py`, `spec.py`, `test_command_generates_apps` |
| REQ-PROD-002 | Reusable named `structures` (dirs + files) referenced by apps | IMPLEMENTED | `spec._parse_structures`, `test_load_valid_spec` |
| REQ-PROD-003 | Named inline `templates` referenced by file entries | IMPLEMENTED | `spec._parse_templates`, `test_template_reference_resolved` |
| REQ-PROD-004 | Per-app files extend/override a structure by path | IMPLEMENTED | `spec._parse_app`, `test_per_app_file_overrides_structure_by_path` |
| REQ-PROD-005 | Placeholder rendering (`app_name/label/class/module` + `context`) in paths, contents, dir names | IMPLEMENTED | `naming.derived_context`, `render` (re-exported), `test_render_*` |
| REQ-PROD-006 | Unknown placeholder raises rather than emitting literal `{{ }}` | IMPLEMENTED | `render.RenderError`, `test_render_unknown_variable_raises` |
| REQ-PROD-007 | Existing files skipped by default; `--force` overwrites | IMPLEMENTED | `forgeapps.py`, `test_existing_file_is_skipped_without_force`, `test_force_overwrites` |
| REQ-PROD-008 | `--dry-run` previews without writing | IMPLEMENTED | `test_command_dry_run_writes_nothing` |
| REQ-PROD-009 | `--base-path` / `--root` / `-c/--config` CLI overrides | IMPLEMENTED | `forgeapps.add_arguments`, `test_command_base_path_override` |
| REQ-PROD-010 | Actionable errors on missing config / invalid YAML / invalid spec | IMPLEMENTED | `forgeapps.handle` (`CommandError`), `test_command_missing_config_errors`, `test_command_invalid_spec_errors` |

## Non-goals

**INFERENCE** (from `README.md`/`AGENTS.md`): not a full project generator, not a
runtime framework; the generation engine itself lives in `chrysa-codegen`, not
here. No web UI. **UNKNOWN** any roadmap toward those.

## Success metrics

**UNKNOWN** — no metrics, analytics, or adoption targets are recorded in the repo.
