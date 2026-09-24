---
name: spec-schema-check
description: "Validate a candidate YAML forge spec against the schema without generating anything. Use before running forgeapps for real, or when a YAML spec fails to load."
when_to_use: "validate yaml spec, check apps.yaml, dry-run forgeapps, spec schema errors, preview generated apps"
disable-model-invocation: false
---

# Spec schema check

Validates a YAML forge document (schema + dry-run plan) with zero side effects,
using the existing `--dry-run` flag on `manage.py forgeapps` — no new code path.

## When to invoke

Before running `forgeapps` for real, or when a `.yaml` spec file fails to parse
or produces unexpected output.

## Steps

1. Ask for (or infer) the path to the candidate YAML file. Default: `apps.yaml`.
2. Run it through Docker per project convention — never on host:
   ```bash
   make docker-test  # if no config path override is needed, this proves the pipeline still works
   ```
   For an ad hoc file, run the dry-run command directly in the same container image
   used by `docker-test`/CI:
   ```bash
   docker run --rm -v "$PWD:/app" -w /app <test-image> \
     python manage.py forgeapps -c <path/to/candidate.yaml> --dry-run
   ```
3. Report the dry-run output verbatim: apps planned, dirs/files that would be
   created, files that would be skipped (already exist).
4. If the command raises `CommandError` (invalid YAML or schema violation),
   surface the exact error message — do not attempt to auto-fix the YAML.

## Non-goals

- Does not write any file — `--dry-run` guarantees this.
- Does not replace `tests/test_golden.py` — that test covers the reference
  `apps.example.yaml`, not arbitrary candidate specs.
