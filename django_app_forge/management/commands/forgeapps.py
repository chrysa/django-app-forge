"""``manage.py forgeapps`` — generate Django apps from a YAML structure file.

This is a thin Django wrapper around the framework-agnostic core
(:mod:`django_app_forge.spec` + :mod:`django_app_forge.generator`).

Examples::

    python manage.py forgeapps                       # reads apps.yaml
    python manage.py forgeapps -c apps/layout.yaml    # custom config
    python manage.py forgeapps --dry-run              # preview, touch nothing
    python manage.py forgeapps --force --base-path apps
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from django.core.management.base import BaseCommand, CommandError, CommandParser

from django_app_forge.generator import ActionKind, apply, plan
from django_app_forge.spec import ProjectSpec, SpecError, load_spec


class Command(BaseCommand):
    help = "Generate one or more Django apps with a custom structure from a YAML file."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "-c",
            "--config",
            default="apps.yaml",
            help="Path to the YAML structure file (default: apps.yaml).",
        )
        parser.add_argument(
            "--root",
            default=".",
            help="Directory the apps are generated under (default: current directory).",
        )
        parser.add_argument(
            "--base-path",
            dest="base_path",
            default=None,
            help="Override the document's base_path.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite files that already exist (default: skip them).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print the planned actions without writing anything.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        config_path = Path(options["config"])
        if not config_path.is_file():
            raise CommandError(f"Config file not found: {config_path}")

        try:
            raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise CommandError(f"Invalid YAML in {config_path}: {exc}") from exc

        try:
            spec = load_spec(raw)
        except SpecError as exc:
            raise CommandError(f"Invalid forge document: {exc}") from exc

        if options["base_path"] is not None:
            spec = ProjectSpec(
                version=spec.version,
                base_path=options["base_path"],
                context=spec.context,
                apps=spec.apps,
            )

        root = Path(options["root"]).resolve()
        dry_run: bool = options["dry_run"]
        force: bool = options["force"]

        try:
            actions = plan(spec, root, force=force)
            performed = apply(actions, dry_run=dry_run)
        except (SpecError, ValueError) as exc:
            raise CommandError(str(exc)) from exc

        skipped = [a for a in actions if a.kind is ActionKind.SKIP]
        written = [a for a in performed if a.kind is ActionKind.WRITE]
        made = [a for a in performed if a.kind is ActionKind.MKDIR]

        for action in actions:
            self.stdout.write(action.describe(root))

        prefix = "Would generate" if dry_run else "Generated"
        self.stdout.write(
            self.style.SUCCESS(
                f"{prefix} {len(spec.apps)} app(s): {len(made)} dir(s), {len(written)} file(s), {len(skipped)} skipped."
            )
        )
        if skipped and not force:
            self.stdout.write(self.style.WARNING("Some files already existed — re-run with --force to overwrite."))
