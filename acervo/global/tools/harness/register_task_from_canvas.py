#!/usr/bin/env python3
"""Register a task from a Canvas YAML file.

Creates a task directory in ACERVO/_tasks/ with:
  - task.yaml (operational state)
  - canvas.yaml (copy of the input canvas)
  - notes.md (empty)
  - links.yaml (empty)
  - events.log (creation event)

Usage:
  python register_task_from_canvas.py --canvas canvas.yaml --title "..." [--primary-microverso slug]
  python register_task_from_canvas.py --from-stdin --title "..."

Environment:
  ACERVO  — path to acervo root (default: ~/exocortex/acervo or ~/.hermes/acervo)
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    # Fallback: basic YAML-like loading for environments without PyYAML
    yaml = None


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


def load_yaml_file(path: Path) -> dict:
    """Load YAML file, stripping frontmatter delimiters if present."""
    text = path.read_text(encoding="utf-8")
    # Strip frontmatter delimiters
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[1]
    if yaml:
        return yaml.safe_load(text) or {}
    # Minimal fallback parser for flat YAML
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ": " in line:
            key, val = line.split(": ", 1)
            result[key.strip()] = val.strip().strip('"').strip("'")
    return result


def generate_task_id(title: str) -> str:
    """Generate a task ID like task_20260603_slug."""
    now = datetime.now(timezone.utc)
    slug = title.lower().replace(" ", "-")[:30]
    # Remove non-alphanumeric except hyphens
    slug = "".join(c for c in slug if c.isalnum() or c == "-")
    slug = slug.strip("-")
    return f"task_{now.strftime('%Y%m%d')}_{slug}"


def compute_content_hash(data: dict) -> str:
    """Compute a stable hash for state_cycle from task content."""
    # Include only stable fields, exclude timestamps and logs
    stable = {
        "title": data.get("title", ""),
        "status": data.get("status", ""),
        "vector": data.get("vector", ""),
        "primary_microverso": data.get("primary_microverso"),
        "decisions": data.get("decisions", {}),
        "artifacts": data.get("artifacts", []),
    }
    raw = json.dumps(stable, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def load_template(acervo: Path) -> str:
    """Load task.yaml template from global/templates."""
    template_path = acervo / "global" / "templates" / "harness-v0.4" / "task.yaml"
    if template_path.is_file():
        return template_path.read_text(encoding="utf-8")
    # Inline fallback
    return """\
task_id: {task_id}
title: "{title}"
status: registered
vector: {vector}

primary_microverso: {primary_microverso}
related_microversos: []

canvas_path: canvas.yaml

personas:
  owner: null
  reviewers: []
  evaluators: []

artifacts: []
routines: []
automations: []

decisions:
  pending: []
  resolved: []

inbox_items: []

approval:
  required: false
  reason: null

evaluation:
  required: false
  reason: null
  status: not_applicable

state_cycle:
  lifecycle_state: registered
  maintenance_state: never_reviewed
  content_hash: {content_hash}
  last_reviewed_hash: null
  last_reviewed_at: null
  last_user_touch_at: {now}
  last_user_touch_session_id: null
  skip_maintenance_if_hash_unchanged: true

created_at: {now}
updated_at: {now}
"""


def main():
    parser = argparse.ArgumentParser(description="Register task from Canvas")
    parser.add_argument("--canvas", type=str, help="Path to canvas YAML file")
    parser.add_argument("--from-stdin", action="store_true", help="Read canvas from stdin")
    parser.add_argument("--title", type=str, required=True, help="Task title")
    parser.add_argument("--primary-microverso", type=str, default="null", help="Primary microverso slug")
    parser.add_argument("--vector", type=str, default="execucao", choices=["evolucao", "execucao", "manutencao"])
    parser.add_argument("--dry-run", action="store_true", help="Print what would be created without writing")
    args = parser.parse_args()

    acervo = resolve_acervo()
    tasks_dir = acervo / "_tasks"

    if not acervo.is_dir():
        print(f"ERROR: Acervo not found at {acervo}", file=sys.stderr)
        sys.exit(1)

    # Load canvas
    canvas_data = {}
    canvas_text = ""
    if args.from_stdin:
        canvas_text = sys.stdin.read()
    elif args.canvas:
        canvas_path = Path(args.canvas)
        if not canvas_path.is_file():
            print(f"ERROR: Canvas file not found: {canvas_path}", file=sys.stderr)
            sys.exit(1)
        canvas_text = canvas_path.read_text(encoding="utf-8")
        canvas_data = load_yaml_file(canvas_path)

    # Generate task ID
    task_id = generate_task_id(args.title)
    task_dir = tasks_dir / task_id
    now = datetime.now(timezone.utc).isoformat()

    # Resolve vector from canvas or arg
    vector = canvas_data.get("vector", args.vector)
    primary_micro = canvas_data.get("microversos", {}).get("primary", args.primary_microverso)
    if primary_micro is None:
        primary_micro = "null"

    # Build task.yaml content
    task_data = {
        "task_id": task_id,
        "title": args.title,
        "vector": vector,
        "primary_microverso": primary_micro,
    }
    content_hash = compute_content_hash(task_data)

    template = load_template(acervo)
    task_yaml = template.format(
        task_id=task_id,
        title=args.title.replace('"', '\\"'),
        vector=vector,
        primary_microverso=primary_micro,
        content_hash=content_hash,
        now=now,
    )

    # Event log entry
    event = f"[{now}] CREATED task_id={task_id} title=\"{args.title}\" vector={vector}\n"

    if args.dry_run:
        print(f"Would create: {task_dir}/")
        print(f"  task.yaml")
        print(f"  canvas.yaml")
        print(f"  notes.md")
        print(f"  links.yaml")
        print(f"  events.log")
        print(f"\ntask_id: {task_id}")
        return

    # Create task directory and files
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "task.yaml").write_text(task_yaml, encoding="utf-8")
    (task_dir / "canvas.yaml").write_text(canvas_text or "# Canvas placeholder\n", encoding="utf-8")
    (task_dir / "notes.md").write_text(f"# Notes — {args.title}\n\n", encoding="utf-8")
    (task_dir / "links.yaml").write_text("# Semantic links\nmicroversos: []\nartifacts: []\ndecisions: []\nroutines: []\nautomations: []\n", encoding="utf-8")
    (task_dir / "events.log").write_text(event, encoding="utf-8")

    print(f"✓ Task registered: {task_dir}")
    print(f"  task_id: {task_id}")
    print(f"  vector: {vector}")
    print(f"  content_hash: {content_hash}")


if __name__ == "__main__":
    main()
