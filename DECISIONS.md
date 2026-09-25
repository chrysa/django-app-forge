# DECISIONS — django-app-forge

> ADR-style record of decisions **verifiable in this repo**. Rationale marked
> **UNKNOWN** where the repo does not record it. This complements the chrysa
> canonical ADR log in `chrysa-lib`/`shared-standards` (referenced, not copied).
>
> Note: the `decisions/` directory holds generic template stubs (DEC-001
> auth-provider, etc.) that are **not** decisions of this project — see
> [`REVIEW.md`](REVIEW.md).

## ADR-DAF-001 — Thin Django adapter over `chrysa-codegen`

- **Status:** Accepted (reflected in code). **Context:** per-project scaffolding
  scripts were duplicated across repos.
- **Decision:** keep only a thin Django layer here; the generation engine
  (`plan`/`apply`/`render`, `to_snake`/`to_pascal`) lives in the shared
  `chrysa-codegen` package and is re-exported.
- **Consequence:** engine changes land upstream; this repo pins a
  `chrysa-codegen` commit. Evidence: `README.md`, `pyproject.toml`.

## ADR-DAF-002 — Core stays import-free of Django

- **Decision:** `spec`/`naming`/`render`/`generator` never import Django, so
  they are unit-testable without a Django app. **Consequence:** Django surface
  is confined to `apps.py` + `forgeapps`. Evidence: `CLAUDE.md`, module source.

## ADR-DAF-003 — Safe-by-default, exact dry-run

- **Decision:** existing files are `SKIP` unless `--force`; `plan()` is pure so
  `apply(dry_run=True)` is exact. **Consequence:** non-destructive default; the
  preview equals the real plan. Evidence: `forgeapps.py`,
  `test_dry_run_writes_nothing`.

## ADR-DAF-004 — Fail-loud rendering

- **Decision:** an unknown placeholder raises `RenderError` rather than emitting
  a literal `{{ … }}`. Evidence: `render.py`, `test_render_unknown_variable_raises`.

## ADR-DAF-005 — Byte-identical golden gate for the engine swap

- **Context:** migrating the engine to `chrysa-codegen` (chrysa-lib#113, lot L1).
- **Decision:** a golden fixture (`tests/golden/django/default/`) locks the
  `{relpath: sha256}` map so post-swap output is byte-identical (AC-L2-05).
  Evidence: `test_golden.py`.

## ADR-DAF-006 — Private-dependency install via BuildKit secret

- **Decision:** fetch private `chrysa-codegen` by mounting a GH token as a
  BuildKit secret and rewriting the git URL in a single layer, dropping the
  gitconfig in the same `RUN` so no token persists in an image layer. Cites
  `chrysa-lib DECISIONS.md D-0004`. Evidence: `Dockerfile.test`, `README.md`.

## Referenced external ADRs (not defined here)

- **D-0004** (chrysa-lib) — private-dep token handling. **UNKNOWN** full text.
- **D-0012** — generated context files (`gen_context_files.py`). **UNKNOWN**
  full text (file location not in this repo).
- **STD-AIORCH-001**, **STD-API-001**, **STD-DATA-001**, **STD-OPS-001** —
  chrysa transverse standards referenced by `CLAUDE.md`; canonical text in
  `shared-standards`.
