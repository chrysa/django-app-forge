---
name: golden-test-update
description: "Regenerate and diff the golden-file fixture (tests/golden/django/default/) after an intentional change to render.py or generator.py output shape. Never invoked automatically."
when_to_use: "golden test failing after intentional generator change, update golden fixture, regenerate sha256map.json"
disable-model-invocation: true
---

# Golden test update

`tests/test_golden.py` byte-compares generator output against a committed
`sha256map.json` fixture. When `render.py` or `generator.py` intentionally
changes output shape, the fixture must be regenerated deliberately — never
silently overwritten by a passing-test run.

## When to invoke

Only when the user explicitly asks to update/regenerate the golden fixture,
typically after confirming `test_golden_output_is_byte_identical` fails due
to an *intended* change (not a regression).

## Steps

1. Confirm with the user that the golden test failure is expected (intended
   output-shape change), not a bug. If unsure, stop and ask — do not proceed.
2. Regenerate the fixture inside Docker (never on host, per `CLAUDE.md`):
   ```bash
   docker run --rm -v "$PWD:/app" -w /app <test-image> python - <<'PY'
   import hashlib, json
   from pathlib import Path
   import yaml
   from django_app_forge.generator import apply, plan
   from django_app_forge.spec import load_spec

   golden_dir = Path("tests/golden/django/default")
   raw = yaml.safe_load((golden_dir / "input.yaml").read_text(encoding="utf-8"))
   spec = load_spec(raw)
   out_dir = Path("/tmp/golden_regen")
   actions = plan(spec, out_dir)
   apply(actions)
   sha256map = {
       str(f.relative_to(out_dir)): hashlib.sha256(f.read_bytes()).hexdigest()
       for f in sorted(out_dir.rglob("*")) if f.is_file()
   }
   (golden_dir / "sha256map.json").write_text(json.dumps(sha256map, indent=2, sort_keys=True) + "\n")
   PY
   ```
3. Show the diff of `sha256map.json` to the user before committing anything.
4. Re-run `pytest tests/test_golden.py` (in Docker) to confirm the fixture now
   matches.
5. Commit the fixture update as its own Conventional Commit
   (`test: update golden fixture for <reason>`), never bundled silently with
   an unrelated change.

## Non-goals

- Does not touch `input.yaml` — only `sha256map.json` is regenerated.
- Does not run outside Docker.
- Never invoked without explicit user confirmation (`disable-model-invocation: true`).
