# Deep-dive — `django-app-forge`

**Purpose (1 phrase):** a Django reusable app that generates one or more Django apps
with a custom directory structure from a single declarative YAML file (`apps.yaml`),
replacing per-project Python scaffolding scripts — the core codegen engine
(`render`, `plan`/`apply`) is delegated to the shared `chrysa-codegen` package.

**Architecture recap (relevant to teardowns):**
- `spec.py` — parse+validate YAML into dataclasses (no Django).
- `naming.py` — snake/Pascal + per-app derived context.
- `render.py` — thin shim re-exporting `chrysa_codegen.render` (`render`, `RenderError`, fails loud on unknown vars).
- `generator.py` — thin shim over `chrysa_codegen.generator`: pure `plan(spec, root, force=)` → list of `Action`; side-effecting `apply()`.
- `management/commands/forgeapps.py` — thin Django wrapper.

The **pure `plan()` → side-effecting `apply()`** split and the **fail-loud render**
are already the two load-bearing design ideas; the reference repos below are the
canonical OSS implementations of exactly those ideas, which makes them useful for
validating and extending the current design rather than importing wholesale.

**Landscape verdict:** this is a niche internal tool (YAML-driven *Django app*
scaffolder). There is no direct external equivalent — the closest OSS is generic
project scaffolders (Copier, PyScaffold, scaffold) and Django startapp-template
repos. 4 references below; all permissive (MIT / MIT+BSD-0). The two Django
startapp-template repos are tiny/archived so they are noted but not given full
teardowns.

---

## copier-org/copier

- **owner/repo:** copier-org/copier
- **stars:** 3,525
- **activity:** very active — pushed 2026-08-14
- **language:** Python
- **licence:** **MIT** (permissive → copiable)
- **file/module of the pattern:** `copier/main.py` (the `Worker` class) + `copier/_render.py` — YAML-config-driven render with a Jinja `undefined` policy.
- **mechanism:** Copier reads `copier.yml` (questions + settings), builds a render
  context, and renders a template tree. The load-bearing detail for this project is
  its **strict-undefined** posture: it configures the Jinja environment with a
  `StrictUndefined`-style behaviour so an unknown variable in a template raises
  rather than silently producing an empty string — the exact contract
  `render.py`/`chrysa_codegen` already enforces via `RenderError`. Copier also
  separates *planning* the file operations from *applying* them (dry-run `--pretend`),
  the same `plan()`/`apply()` split.
- **portable snippet (~12 lines) — strict-undefined render, MIT-safe to copy:**
  ```python
  from jinja2 import Environment, StrictUndefined
  from jinja2.exceptions import UndefinedError

  def render_strict(template_str: str, context: dict) -> str:
      env = Environment(undefined=StrictUndefined, keep_trailing_newline=True)
      try:
          return env.from_string(template_str).render(**context)
      except UndefinedError as exc:
          # fail loud, like copier / chrysa_codegen.RenderError
          raise RuntimeError(f"unknown template variable: {exc}") from exc
  ```
- **integration steps:** (1) `render.py` currently uses a custom `{{ var }}`
  substitution in `chrysa-codegen`; if richer templating is ever needed (loops,
  filters), adopt Copier's `StrictUndefined` Jinja env inside `chrysa_codegen.render`
  and keep raising `RenderError`. (2) Consider Copier's `--pretend` dry-run flag as
  precedent for a `forgeapps --dry-run` that prints `plan()` without `apply()`.
- **gotchas:** Copier pulls in a large dependency surface (Jinja2, pydantic,
  questionary, plumbum) — do **not** add it as a dependency; reimplement the ~10-line
  strict-undefined pattern only. Copier's `_render` couples rendering to its
  question/answers-file lifecycle; that state machine is irrelevant here.

---

## pyscaffold/pyscaffold

- **owner/repo:** pyscaffold/pyscaffold
- **stars:** 2,264
- **activity:** active — pushed 2026-08-10
- **language:** Python
- **licence:** **MIT** for the code; generated template files are **BSD-0-Clause**
  (both permissive → copiable; note the dual-license split if you copy template text).
- **file/module of the pattern:** `src/pyscaffold/structure.py` (the `Structure`
  type + `merge`/`create_structure`) and `src/pyscaffold/actions.py`.
- **mechanism:** PyScaffold models the entire project as a nested **dict describing
  the file tree** (`Structure`), then runs an ordered pipeline of pure **actions**
  `(struct, opts) -> (struct, opts)` that transform that description; a single final
  action walks the dict and writes files. This is precisely `django-app-forge`'s
  `plan()` (build a `list[Action]`) → `apply()` (touch disk) separation, but taken
  further: PyScaffold makes the *whole plan* a data structure that extensions can
  rewrite before any I/O — the model for making `chrysa_codegen` extensible.
- **portable snippet (~14 lines) — declarative tree → actions, MIT-safe pattern:**
  ```python
  # A file tree as pure data; leaves are (content, update_rule)
  Structure = dict  # {name: Structure | (content, rule)}

  def create_structure(struct, prefix=""):
      for name, node in struct.items():
          path = f"{prefix}/{name}"
          if isinstance(node, dict):
              yield ("mkdir", path)
              yield from create_structure(node, path)
          else:
              content, _rule = node
              yield ("write", path, content)  # apply() consumes these tuples
  ```
- **integration steps:** (1) The current `plan()` returns a flat `list[Action]`;
  PyScaffold's insight is to let *extensions* rewrite the structure/action list
  before `apply()`. If `chrysa-codegen` grows plugins (e.g. add a `tests/` layout,
  inject `admin.py`), model them as `(actions, ctx) -> (actions, ctx)` transforms
  chained before `apply()`. (2) Adopt PyScaffold's per-leaf **update rule**
  (`NO_OVERWRITE` / `NO_CREATE`) idea to refine the existing `force=` boolean into
  per-file policy.
- **gotchas:** PyScaffold's action pipeline uses a global setuptools/PyPI project
  worldview (git init, tox, setup.cfg) — most actions are irrelevant to app-level
  Django scaffolding; take only the `Structure`+action-transform shape. The BSD-0
  applies to their *template payloads*, not the engine code.

---

## hay-kot/scaffold

- **owner/repo:** hay-kot/scaffold
- **stars:** 177
- **activity:** very active — pushed 2026-08-15
- **language:** Go
- **licence:** **MIT** (permissive → concepts copiable; it's Go so port, don't copy code)
- **file/module of the pattern:** `.scaffold/scaffold.yaml` schema + the
  `rwfs`/engine packages — **in-project component scaffolding** driven by a
  per-template YAML with questions and a rendered file tree.
- **mechanism:** Unlike Copier/Cookiecutter (whole-project bootstrap), `scaffold` is
  designed to generate *components inside an existing project* (a controller, a
  module) from a YAML spec — conceptually the same niche as `forgeapps` generating an
  app inside a Django project. It renders a templated directory tree into the current
  repo, and supports **injecting into existing files** at marker points (its "inject"
  feature) rather than only creating new files.
- **portable snippet (~10 lines) — the inject-at-marker idea, ported to Python:**
  ```python
  # Add an app to INSTALLED_APPS by inserting at a marker instead of overwriting.
  MARKER = "# scaffold:apps"  # left in settings.py

  def inject_after_marker(text: str, marker: str, line: str) -> str:
      out = []
      for row in text.splitlines():
          out.append(row)
          if marker in row:
              out.append(line)
      return "\n".join(out) + "\n"
  ```
- **integration steps:** (1) `forgeapps` today only *creates* app files; scaffold's
  inject pattern is the blueprint for a follow-up feature that also **registers** the
  generated app (append to `INSTALLED_APPS`, wire a `urls.py` include) by inserting at
  a sentinel comment — add this as a new `ActionKind.INJECT` in `chrysa_codegen`.
  (2) Its `scaffold.yaml` question schema is worth mirroring if `apps.yaml` ever needs
  interactive prompts.
- **gotchas:** It's Go — no code reuse, only design. Its templating is Go
  `text/template` (different delimiters/semantics from `{{ var }}`); don't copy
  template syntax. Inject-at-marker is fragile if the marker is edited away — guard
  with "marker missing → fail loud", consistent with the project's fail-loud ethos.

---

## Noted-but-not-full: Django startapp-template repos

- **GriceTurrble/django-app-template** — stars 2, **archived** (last push 2021-04-25),
  no SPDX license detected (treat as all-rights-reserved → **do NOT copy files**;
  reference the *idea* only). This is the vanilla mechanism `django-app-forge`
  supersedes: a directory passed to `django-admin startapp --template`, using Django's
  built-in `{{ }}`/`{% templatetag %}` rendering. Useful only to confirm the baseline
  the project improves on (multi-app, YAML-declared, custom structure vs. one fixed
  template).
- **jondot/hygen** — stars 5,931, MIT, but **stale** (last push 2024-07-09) and
  JavaScript. Relevant idea: front-matter-per-template-file (`to:`, `inject:`,
  `skip_if:`) so each template declares its own destination and inject rules — an
  alternative to a central `apps.yaml` if per-file metadata is ever wanted. Port the
  concept, not the code.

---

## Cross-cutting takeaways

1. **Fail-loud strict render** is validated by Copier's `StrictUndefined` — the
   existing `RenderError` contract is the industry-standard choice; if templating
   grows, adopt Copier's Jinja strict-undefined env (10 lines) rather than a new dep.
2. **plan()/apply() split** is validated by both Copier (`--pretend`) and PyScaffold
   (structure-as-data + action pipeline). Next evolution: make the action list
   *rewritable by extensions* before `apply()` (PyScaffold model) and expose a
   `--dry-run` (Copier model).
3. **Inject-into-existing-files** (hay-kot/scaffold, hygen) is the missing capability:
   a future `ActionKind.INJECT` to auto-register generated apps in `INSTALLED_APPS`/urls.
4. **Licence posture:** Copier, PyScaffold (code), scaffold, hygen are all MIT →
   patterns/snippets copiable. PyScaffold *template payloads* are BSD-0 (also fine).
   GriceTurrble/django-app-template has **no license + archived → reimplement only**.
