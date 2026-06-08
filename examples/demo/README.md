# django-app-forge — runnable demo

A minimal Django project showing how `manage.py forgeapps` scaffolds Django apps
from a single declarative `apps.yaml`.

## What it shows

- `django_app_forge` in `INSTALLED_APPS` (`demo_project/settings.py`) so the
  `forgeapps` command is available.
- An `apps.yaml` that defines a reusable `ddd` structure (a `services/`,
  `tests/`, `migrations/` layout) and two apps, `billing` and `catalog`, with
  `catalog` adding an extra per-app file.
- Named templates with placeholders (`{{ app_class }}`, `{{ app_module }}`,
  `{{ author }}`) expanded per app.

## Run it

From the repository root (use Docker or a virtualenv — never system Python):

```bash
pip install -e ".[dev]"
```

Then, from this directory (`examples/demo/`):

```bash
# 1. Preview — prints the planned tree, writes nothing.
python manage.py forgeapps --dry-run

# 2. Generate the apps under ./apps/.
python manage.py forgeapps

# 3. Re-run — existing files are skipped (idempotent)...
python manage.py forgeapps

# 4. ...unless you force an overwrite.
python manage.py forgeapps --force
```

Inspect the result:

```bash
find apps -type f
```

You'll see `apps/billing/` and `apps/catalog/` with `apps.py`, `models.py`,
`services/`, `tests/`, and `migrations/` — `catalog` also gets
`services/pricing.py` from its per-app `files:` entry. The generated `apps/`
tree is gitignored; delete it and re-run any time.
