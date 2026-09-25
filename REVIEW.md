# REVIEW — django-app-forge (documentation audit)

> Read-only documentation audit. No source/test/config changed. Findings for the
> owner.

## Summary

`django-app-forge` is a small, well-tested Django app scaffolder (thin adapter
over the private `chrysa-codegen` engine). Code, README, `CLAUDE.md`, and
`AGENTS.md` are accurate and consistent. The main documentation debt is a large
set of **generic docs-structure boilerplate stubs** that do not describe this
project.

## Contradictions & mismatches

1. **Boilerplate docs that misdescribe the project.** The `docs/`, `decisions/`,
   `postmortems/`, `schemas/`, `workflows/`, `prompts/`, `legal/` trees, and the
   `tests/*.md` catalogues, contain template placeholders for an unrelated
   web/SaaS product: auth-provider decisions, payment/webhook postmortems,
   payment/user/project JSON schemas, billing/auth/notification flows,
   sales/support/onboarding agent prompts, CGU/legal notices. This repo has no
   payments, auth, webhooks, or agents. These are unfilled scaffolding from
   `shared-standards/templates/docs-structure` (README "Documentation map" says
   as much: "Files marked `status: stub` are placeholders to fill in").
   - **Impact:** an agent or reader trusting `docs/security.md`,
     `decisions/DEC-001`, `schemas/payment.schema.json`, etc. would be misled.
   - **Recommendation (PROPOSAL, not applied — outside this pass's write scope):**
     either fill the stubs with real content for this project or delete the
     inapplicable ones. The new root docs (PRD/TRD/ARCHITECTURE/…) supersede them.

2. **`examples/perfect_*.py`** (FastAPI-style `perfect_api_view`,
   `perfect_repository`, `perfect_serializer`, `perfect_viewset`, …) are generic
   "reference implementation" boilerplate, not examples of using this scaffolder.
   The real, project-specific example is `examples/demo/` (runnable Django
   project) — which is correct and matches the code.

3. **Machine-coupled path in `.mcp.json`.** The `graphify` server hardcodes
   `/home/anthony/…/graph.json`, contrary to the chrysa machine-agnostic
   standard. Config hygiene, not correctness. See `SECURITY.md`.

## Things that are correct and good

- README, `apps.example.yaml`, and `examples/demo/` agree with the code.
- Strong test discipline: 28 tests + a byte-identical golden gate; coverage
  gate ≥85%; Docker/pre-commit-only workflow; typed library.
- Clean private-dependency handling (BuildKit secret, no persisted token).
- No hardcoded secrets.

## Documentation debt (prioritized)

1. Resolve the boilerplate stub trees (fill or remove) — highest signal risk.
2. Populate `CHANGELOG.md` on first release (currently `[Unreleased]` only).
3. Fill `tests/*.md` scenario catalogues or drop them.
4. Relativize the `.mcp.json` graphify path.

## Docs generated this pass (root only)

`PRD.md`, `TRD.md`, `ARCHITECTURE.md`, `REQUIREMENTS.md`, `CONSTRAINTS.md`,
`DECISIONS.md`, `TESTING.md`, `SECURITY.md`, `GLOSSARY.md`, `REVIEW.md`.

**Skipped** (recorded): `OBSERVABILITY.md` — no runtime, logging, metrics, or
tracing in a build-time scaffolder (nothing verifiable to document);
`ROADMAP.md` — no real roadmap/backlog data in-repo (only stub
`docs/feature-backlog.md`), so any roadmap would be invented.
