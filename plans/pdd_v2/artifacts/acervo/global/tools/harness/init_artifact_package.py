#!/usr/bin/env python3
"""Initialize an artifact package in ACERVO/_artifacts/items/.

Creates the canonical artifact directory structure:
  {artifact_id}/
  ├── source/
  ├── assets/
  ├── exports/
  ├── evaluations/
  ├── receipts/
  └── manifest.json

Usage:
  python init_artifact_package.py --title "..." [--task-id task_xxx] [--microverso slug]
  python init_artifact_package.py --title "..." --source-md /path/to/source.md

Environment:
  ACERVO  — path to acervo root (default: ~/exocortex/acervo or ~/.hermes/acervo)
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


def resolve_acervo() -> Path:
    """Resolve acervo root from env or default locations."""
    if env := os.environ.get("ACERVO"):
        return Path(env)
    exo_home = os.environ.get("EXOCORTEX_HOME", os.path.expanduser("~/exocortex"))
    candidate = Path(exo_home) / "acervo"
    if candidate.is_dir():
        return candidate
    hermes_home = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
    return Path(hermes_home) / "acervo"


def generate_artifact_id(title: str) -> str:
    """Generate artifact ID like art_20260603_150000_slug."""
    now = datetime.now(timezone.utc)
    slug = title.lower().replace(" ", "-")[:30]
    slug = "".join(c for c in slug if c.isalnum() or c == "-")
    slug = slug.strip("-")
    return f"art_{now.strftime('%Y%m%d_%H%M%S')}_{slug}"


def build_manifest(
    artifact_id: str,
    title: str,
    task_id: str | None,
    primary_microverso: str | None,
    related_microversos: list[str],
    artifact_type: str,
    source_type: str,
    scope: str,
) -> dict:
    """Build manifest.json content from canonical template."""
    now = datetime.now(timezone.utc).isoformat()
    slug = artifact_id.split("_", 3)[-1] if "_" in artifact_id else artifact_id

    return {
        "artifact_id": artifact_id,
        "canonical_slug": slug,
        "friendly_name": title,
        "publication_names": {},
        "title": title,
        "status": "draft",
        "artifact_type": artifact_type,
        "source_type": source_type,
        "task_id": task_id,
        "primary_microverso": primary_microverso,
        "related_microversos": related_microversos,
        "scope": scope,
        "owner": {
            "type": "task" if task_id else "microverso",
            "id": task_id or primary_microverso,
        },
        "personas_involved": [],
        "semantic_links": [],
        "source_path": "source/source.md",
        "exports": [],
        "evaluation": {
            "status": "pending",
            "personas": [],
            "reports": [],
            "incorporated_suggestions": [],
            "pending_suggestions": [],
        },
        "publication": {
            "drive": {
                "status": "not_published",
                "receipt_path": None,
            },
        },
        "provenance": {
            "created_by": "exocortex",
            "created_at": now,
            "origin": "conversation",
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Initialize artifact package")
    parser.add_argument("--title", type=str, required=True, help="Artifact title (friendly name)")
    parser.add_argument("--task-id", type=str, default=None, help="Related task ID")
    parser.add_argument("--microverso", type=str, default=None, help="Primary microverso slug")
    parser.add_argument("--related-microversos", type=str, nargs="*", default=[], help="Related microverso slugs")
    parser.add_argument("--artifact-type", type=str, default="document",
                        choices=["document", "report", "deck", "html", "pdf", "image", "zip", "code", "mixed"])
    parser.add_argument("--source-type", type=str, default="markdown",
                        choices=["markdown", "html", "pptx", "xlsx", "external", "mixed"])
    parser.add_argument("--scope", type=str, default="micro", choices=["micro", "shared", "global"])
    parser.add_argument("--source-md", type=str, default=None, help="Path to initial source.md to copy")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be created")
    args = parser.parse_args()

    acervo = resolve_acervo()
    artifacts_dir = acervo / "_artifacts" / "items"

    if not acervo.is_dir():
        print(f"ERROR: Acervo not found at {acervo}", file=sys.stderr)
        sys.exit(1)

    artifact_id = generate_artifact_id(args.title)
    artifact_dir = artifacts_dir / artifact_id

    manifest = build_manifest(
        artifact_id=artifact_id,
        title=args.title,
        task_id=args.task_id,
        primary_microverso=args.microverso,
        related_microversos=args.related_microversos,
        artifact_type=args.artifact_type,
        source_type=args.source_type,
        scope=args.scope,
    )

    if args.dry_run:
        print(f"Would create: {artifact_dir}/")
        print(f"  source/source.md")
        print(f"  assets/")
        print(f"  exports/")
        print(f"  evaluations/")
        print(f"  receipts/")
        print(f"  manifest.json")
        print(f"\nartifact_id: {artifact_id}")
        print(f"\nmanifest.json:\n{json.dumps(manifest, indent=2, ensure_ascii=False)}")
        return

    # Create directory structure
    (artifact_dir / "source").mkdir(parents=True, exist_ok=True)
    (artifact_dir / "assets").mkdir(exist_ok=True)
    (artifact_dir / "exports").mkdir(exist_ok=True)
    (artifact_dir / "evaluations").mkdir(exist_ok=True)
    (artifact_dir / "receipts").mkdir(exist_ok=True)

    # Write manifest
    (artifact_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # Write or copy source
    if args.source_md and Path(args.source_md).is_file():
        shutil.copy2(args.source_md, artifact_dir / "source" / "source.md")
    else:
        (artifact_dir / "source" / "source.md").write_text(
            f"# {args.title}\n\n<!-- Source content goes here -->\n",
            encoding="utf-8",
        )

    print(f"✓ Artifact package initialized: {artifact_dir}")
    print(f"  artifact_id: {artifact_id}")
    print(f"  status: draft")
    print(f"  manifest: {artifact_dir / 'manifest.json'}")


if __name__ == "__main__":
    main()
