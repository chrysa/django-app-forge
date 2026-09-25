# SECURITY — django-app-forge

> Owner-facing security notes. This is a **documentation** pass: no code was
> changed. Findings are classified; the owner decides remediation. Secrets are
> never reproduced here — only their location and nature.

## Threat surface (FACT / INFERENCE)

- **INFERENCE** Small blast radius: a developer-run scaffolder / build-time
  library. No network server, no user auth, no database at runtime, no request
  handling. Inputs are a local YAML file and CLI flags.
- **FACT** YAML is parsed with `yaml.safe_load` (not `yaml.load`) — no arbitrary
  object construction. Evidence: `forgeapps.py`.
- **FACT** `apply()` writes files under a resolved `--root`; `--force` opts into
  overwrite, default skips. Evidence: `forgeapps.py`.

## Secret handling

- **FACT — no hardcoded secrets found.** A scan of source, `pyproject.toml`,
  `.mcp.json`, and `Dockerfile.test` for token/key/PEM patterns returned nothing.
- **FACT** `.mcp.json` references credentials only via env interpolation:
  `${GITHUB_TOKEN}` and `${NOTION_API_KEY}` — no literal values committed.
  [REDACTED nature: env-var placeholders; location: `.mcp.json`.]
- **FACT (good practice)** `Dockerfile.test` fetches the private
  `chrysa-codegen` by mounting a GH token as a BuildKit secret and removing the
  generated gitconfig in the same `RUN`, so the token does not persist in any
  image layer. Evidence: `Dockerfile.test` (per chrysa-lib D-0004).
- **FACT** Local defensive controls present: `.claude/hooks/secret-scanner.cjs`,
  hookify `block-env-edits`, `check-no-env-files.cjs`; pre-commit config exists.

## Findings

| Severity | Finding | Location | Note |
|----------|---------|----------|------|
| INFO | Placeholder-only credential references (env interpolation) | `.mcp.json` | Expected; not a leak |
| LOW | Path-traversal is not explicitly bounded in the reviewed adapter | user-supplied `path`/`dirs` in the YAML + `--root` | File paths come from a **local, developer-authored** YAML; the write engine lives in `chrysa-codegen` (not in this repo) — traversal handling is **UNKNOWN** here. Trust boundary is low (self-authored input), but if forge docs are ever accepted from untrusted sources, verify the engine confines writes under `root`. |
| LOW | Hardcoded absolute machine path (not a secret) | `.mcp.json` (`graphify` server args) | `/home/anthony/…/graph.json` couples the file to one machine, contrary to the chrysa "machine-agnostic / no hardcoded machine paths" standard. Not a security leak; portability/config hygiene. Owner may relativize it. |

**No HIGH or CRITICAL findings.** Nothing to fix in this repo's code for the
documented scope.

## Recommendations (PROPOSAL — not applied)

- If untrusted forge documents ever become an input, add/verify an explicit
  "writes must stay under `--root`" guard (likely in `chrysa-codegen`).
- Keep the BuildKit-secret pattern for any future CI/image that fetches
  `chrysa-lib`.

## Standards linkage

`CLAUDE.md` embeds the chrysa security canon (server-side validation, security
scanning as a CI/pre-commit gate, no hardcoded secrets). Canonical text lives in
`shared-standards`; this repo inherits it.
