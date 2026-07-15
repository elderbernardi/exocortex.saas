#!/usr/bin/env python3
"""
migrate_frontmatter_v2.py — Migrate Acervo frontmatter from v1.0.0 to schema v0.2 (ADR-023)

Upgrades files already on the OKF v0.1 superset schema (ADR-013, produced by
migrate_frontmatter.py) to schema v0.2 as specified in:
  - docs/plans/2026-07-03_memory-v2-spec/13-artifacts/SCHEMA-v0.2.md
  - docs/plans/2026-07-03_memory-v2-spec/05-object-model.md §2 (migration rules)

Per-file transformation (IDEMPOTENT — a file carrying `schema:` is never touched):
  1. Add `schema: acervo/v0.2` as the FIRST frontmatter key. Files that already
     have a `schema` key are counted as already-v2 and skipped entirely.
  2. Derive `status` (inserted after `class`), unless already present:
       quarantined_at present  → quarantined
       deprecated: true        → deprecated
       superseded_by present   → superseded
       otherwise               → active
  3. Default `epistemic` by `type` when absent — ONLY for the epistemic types
     decision/reflection/knowledge/context:
       decision → decision, reflection → interpretation,
       knowledge → fact, context → fact
     Other types are left without `epistemic` (Tier 1 is WARN for them).
  4. Remap `confidence` from the v1 vocabulary (low/medium/high) to the v0.2
     vocabulary (high/likely/possible/low). Conservative mapping:
       high → high, medium → likely, low → low
     `medium` maps to `likely` (not `possible`) because v1 `medium` was the
     working default for reasonably-supported claims; `possible` in v0.2
     signals genuine doubt. Absent confidence stays absent. Values outside
     the v1 vocabulary are left untouched (validator will WARN).
  5. Derive `nature` from the directory when absent
     (micro/{slug}/{nature}/... or global|shared/{nature}/...). When `nature`
     is present but differs from the directory, it is NOT changed — the file
     is flagged needs-review instead (V2 rule: nature must equal directory).

Deliberately NOT done (migration must not invent provenance):
  - `extraction`, `sources`, `observed_at` are never fabricated.
  - `timestamp` is kept (dual-write during the transition; v0.2 derives it
    from `created_at` at OKF export time — removal happens in a later pass).
  - `excrtx_type` and every other existing field are preserved verbatim,
    in their original order.

Usage:
    python3 scripts/migrate_frontmatter_v2.py --dir acervo --dry-run --report
    python3 scripts/migrate_frontmatter_v2.py --file acervo/micro/x/knowledge/y.md
    python3 scripts/migrate_frontmatter_v2.py --dir ~/.hermes/acervo

Exit codes:
    0 — migration completed (or dry-run completed) with no errors
    1 — one or more files had errors during migration
    2 — target file/directory not found
"""

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required. Install with: pip install pyyaml")


# ═══════════════════════════════════════════════════════════════════════════
#  YAML Loader / Dumper (same approach as migrate_frontmatter.py)
# ═══════════════════════════════════════════════════════════════════════════

class FrontmatterLoader(yaml.SafeLoader):
    """SafeLoader variant that does not auto-parse dates/timestamps.

    Without this, PyYAML converts ``created_at: 2026-06-11T00:00:00Z`` into a
    ``datetime`` object. We need the raw string so the exact textual
    representation round-trips unchanged.
    """


_clean_resolvers = {}
for _ch, _resolvers in list(yaml.SafeLoader.yaml_implicit_resolvers.items()):
    _clean_resolvers[_ch] = [
        (tag, regexp) for tag, regexp in _resolvers
        if tag != "tag:yaml.org,2002:timestamp"
    ]
FrontmatterLoader.yaml_implicit_resolvers = _clean_resolvers


class FrontmatterDumper(yaml.SafeDumper):
    """Dumper that uses flow-style for simple scalar lists (``tags: [a, b]``)."""


def _represent_list(dumper, data):
    """Use flow style for lists of simple scalars; block style otherwise."""
    if len(data) == 0:
        return dumper.represent_sequence(
            "tag:yaml.org,2002:seq", [], flow_style=True
        )
    if all(isinstance(x, (str, int, float, bool)) or x is None for x in data):
        return dumper.represent_sequence(
            "tag:yaml.org,2002:seq", data, flow_style=True
        )
    return dumper.represent_sequence(
        "tag:yaml.org,2002:seq", data, flow_style=False
    )


FrontmatterDumper.add_representer(list, _represent_list)

_dumper_resolvers = {}
for _ch, _resolvers in list(yaml.SafeDumper.yaml_implicit_resolvers.items()):
    _dumper_resolvers[_ch] = [
        (tag, regexp) for tag, regexp in _resolvers
        if tag != "tag:yaml.org,2002:timestamp"
    ]
FrontmatterDumper.yaml_implicit_resolvers = _dumper_resolvers


# ═══════════════════════════════════════════════════════════════════════════
#  Constants — Migration Tables (SCHEMA-v0.2.md + 05-object-model.md §2)
# ═══════════════════════════════════════════════════════════════════════════

SCHEMA_VALUE = "acervo/v0.2"

# Directories excluded from migration — kept in sync with
# validate_frontmatter.py DEFAULT_EXCLUDE_DIRS / DEFAULT_EXCLUDE_NAMES.
EXCLUDED_DIRS = frozenset({
    "_artifacts", "raw", "_archive", ".quarantine",
    "_inbox", "_tasks", "_routines", "_automations",
    "_template",
    "_retired",
    "_ops_snapshots", "_fixture",
    "macro",
})
EXCLUDED_NAMES = frozenset({"README.md"})

# `epistemic` defaults by `type` — ONLY the four types below get a default.
TYPE_EPISTEMIC_DEFAULTS = {
    "decision": "decision",
    "reflection": "interpretation",
    "knowledge": "fact",
    "context": "fact",
}

# Conservative v1 → v0.2 confidence vocabulary mapping (see module docstring).
CONFIDENCE_MAP = {
    "high": "high",
    "medium": "likely",
    "low": "low",
}

# v0.2: `type` must match the home directory (V2-020). Migration aligns it.
DIR_TO_TYPE = {
    "context": "context", "knowledge": "knowledge", "decisions": "decision",
    "episodes": "episode", "entities": "entity", "intentions": "intention",
    "workflows": "workflow", "contracts": "contract", "reflections": "reflection",
    "persona": "persona", "prompts": "prompt", "templates": "template",
    "tools": "tool", "skills": "skill", "cross-refs": "knowledge",
}

# v1 files used free-form status values (ADR convention). v0.2 has an enum.
V2_STATUS_ENUM = {"draft", "active", "superseded", "deprecated", "quarantined", "archived"}
LEGACY_STATUS_MAP = {"accepted": "active", "proposed": "draft", "rejected": "deprecated"}

# Directory names that act as nature dirs inside a scope container
# (v0.2 object catalog homes + legacy dirs).
NATURE_DIRS = frozenset({
    "context", "knowledge", "decisions", "workflows", "contracts",
    "reflections", "episodes", "entities", "intentions", "persona",
    "prompts", "templates", "tools", "skills", "memories", "_meta",
})

# Scope containers: micro/{slug}/{nature}/..., global/{nature}/...,
# shared/{nature}/...
SCOPE_MICRO = "micro"
SCOPE_FLAT = frozenset({"global", "shared"})


# ═══════════════════════════════════════════════════════════════════════════
#  Path / Scope Helpers
# ═══════════════════════════════════════════════════════════════════════════

def is_excluded(path: Path, base: Path) -> bool:
    """True if *path* lives inside an excluded directory relative to *base*."""
    try:
        rel = path.relative_to(base)
    except ValueError:
        return True
    if any(part in EXCLUDED_DIRS for part in rel.parts[:-1]):
        return True
    if rel.parts[-1] in EXCLUDED_NAMES:
        return True
    return False


def derive_nature_from_path(filepath: Path) -> str | None:
    """Derive the nature directory from the file's path, or None.

    Patterns: ``micro/{slug}/{nature}/...`` and ``global|shared/{nature}/...``.
    The candidate component must be a known nature dir and must not be the
    filename itself.
    """
    parts = filepath.parts
    last = len(parts) - 1  # index of the filename
    for i, part in enumerate(parts[:-1]):
        if part == SCOPE_MICRO:
            candidate_idx = i + 2
        elif part in SCOPE_FLAT:
            candidate_idx = i + 1
        else:
            continue
        if candidate_idx < last and parts[candidate_idx] in NATURE_DIRS:
            return parts[candidate_idx]
    return None


# ═══════════════════════════════════════════════════════════════════════════
#  Derivation Logic
# ═══════════════════════════════════════════════════════════════════════════

def derive_status(data: dict) -> str:
    """Derive v0.2 ``status`` from v1 conditional lifecycle fields."""
    if data.get("quarantined_at") is not None:
        return "quarantined"
    if data.get("deprecated") is True:
        return "deprecated"
    if data.get("superseded_by") is not None:
        return "superseded"
    return "active"


# ═══════════════════════════════════════════════════════════════════════════
#  Frontmatter Extraction & Serialization (same as migrate_frontmatter.py)
# ═══════════════════════════════════════════════════════════════════════════

def extract_frontmatter(text: str) -> tuple[dict | None, str, bool]:
    """Extract frontmatter and body from markdown text.

    Returns ``(data, body, had_frontmatter)``.
    If the file has no frontmatter, returns ``(None, text, False)``.
    """
    lines = text.split("\n")

    if not lines or lines[0].rstrip("\r") != "---":
        return None, text, False

    closing_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].rstrip("\r") == "---":
            closing_idx = idx
            break

    if closing_idx is None:
        return None, text, False

    yaml_text = "\n".join(lines[1:closing_idx])
    body = "\n".join(lines[closing_idx + 1:])

    try:
        data = yaml.load(yaml_text, Loader=FrontmatterLoader)
    except yaml.YAMLError:
        return None, body, True

    if data is None:
        data = {}
    if not isinstance(data, dict):
        return None, body, True

    return data, body, True


def serialize_frontmatter(data: dict) -> str:
    """Serialize *data* dict to a YAML string (no leading/trailing newlines)."""
    yaml_text = yaml.dump(
        data,
        Dumper=FrontmatterDumper,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=10000,  # prevent line wrapping
    )
    return yaml_text.rstrip("\n")


# ═══════════════════════════════════════════════════════════════════════════
#  Migration Engine
# ═══════════════════════════════════════════════════════════════════════════

def migrate_file(filepath: Path, dry_run: bool) -> dict:
    """Migrate a single markdown file to schema v0.2.

    Returns a result dict with keys:
      ``path``, ``action`` (migrated|already-v2|skipped|error),
      ``changes`` (list[str]), ``review`` (list[str] — needs-review notes).
    """
    result = {
        "path": str(filepath),
        "action": "skipped",
        "changes": [],
        "review": [],
    }

    try:
        original_text = filepath.read_text(encoding="utf-8")
    except OSError as exc:
        result["action"] = "error"
        result["changes"].append(f"cannot read file: {exc}")
        return result

    data, body, had_fm = extract_frontmatter(original_text)

    if not had_fm:
        result["changes"].append("no frontmatter — not a v1 object, left as-is")
        return result  # skipped

    if data is None:
        result["action"] = "error"
        result["changes"].append("frontmatter is not valid YAML mapping")
        return result

    # ── Idempotency gate: already on v0.2 (or any schema) → never touch ────
    if "schema" in data:
        result["action"] = "already-v2"
        return result

    # ── Derive new values ───────────────────────────────────────────────────
    changes = result["changes"]
    changes.append(f"schema: {SCHEMA_VALUE}")

    add_status = "status" not in data
    status = derive_status(data) if add_status else None
    if add_status:
        changes.append(f"status: {status}")

    # status normalization: v1 free-form values -> v0.2 enum (V2-017)
    new_status_value = None
    if not add_status:
        cur_status = data.get("status")
        if isinstance(cur_status, str) and cur_status not in V2_STATUS_ENUM:
            if cur_status in LEGACY_STATUS_MAP:
                new_status_value = LEGACY_STATUS_MAP[cur_status]
                changes.append(f"status: {cur_status} → {new_status_value}")
            else:
                result["review"].append(
                    f"status {cur_status!r} not in v0.2 enum and not mappable — left unchanged"
                )

    # type alignment: v0.2 requires type == directory type (V2-020)
    obj_type = data.get("type")
    dir_nature_for_type = derive_nature_from_path(filepath.resolve())
    mapped_type = DIR_TO_TYPE.get(dir_nature_for_type) if dir_nature_for_type else None
    new_type_value = None
    if (
        mapped_type is not None
        and isinstance(obj_type, str)
        and obj_type not in (mapped_type, "conflict")
    ):
        new_type_value = mapped_type
        changes.append(f"type: {obj_type} → {mapped_type} (aligned to directory)")
    final_type = new_type_value or obj_type

    add_epistemic = (
        "epistemic" not in data
        and isinstance(final_type, str)
        and final_type in TYPE_EPISTEMIC_DEFAULTS
    )
    epistemic = TYPE_EPISTEMIC_DEFAULTS[final_type] if add_epistemic else None
    if add_epistemic:
        changes.append(f"epistemic: {epistemic} (default for type: {final_type})")

    # confidence remap (only values in the v1 vocabulary; others untouched)
    old_conf = data.get("confidence")
    new_conf = None
    if isinstance(old_conf, str) and old_conf in CONFIDENCE_MAP:
        if CONFIDENCE_MAP[old_conf] != old_conf:
            new_conf = CONFIDENCE_MAP[old_conf]
            changes.append(f"confidence: {old_conf} → {new_conf}")

    # nature: derive from directory when absent; flag mismatch when present
    dir_nature = derive_nature_from_path(filepath.resolve())
    existing_nature = data.get("nature")
    add_nature = existing_nature is None and dir_nature is not None
    if add_nature:
        changes.append(f"nature: {dir_nature} (derived from directory)")
    elif (
        isinstance(existing_nature, str)
        and dir_nature is not None
        and existing_nature != dir_nature
    ):
        result["review"].append(
            f"nature {existing_nature!r} != directory {dir_nature!r} — left unchanged"
        )

    # ── Rebuild frontmatter: schema first, insertions in place ──────────────
    ordered = {"schema": SCHEMA_VALUE}
    status_placed = not add_status
    epistemic_placed = not add_epistemic

    for key, value in data.items():
        if key == "confidence" and new_conf is not None:
            value = new_conf
        if key == "type" and new_type_value is not None:
            value = new_type_value
        if key == "status" and new_status_value is not None:
            value = new_status_value
        ordered[key] = value
        if key == "class" and not status_placed:
            ordered["status"] = status
            status_placed = True
            if not epistemic_placed:
                ordered["epistemic"] = epistemic
                epistemic_placed = True
        elif key == "status" and not epistemic_placed:
            ordered["epistemic"] = epistemic
            epistemic_placed = True

    # Fallbacks when `class`/`status` anchors are missing: append at the end.
    if not status_placed:
        ordered["status"] = status
        if not epistemic_placed:
            ordered["epistemic"] = epistemic
            epistemic_placed = True
    if not epistemic_placed:
        ordered["epistemic"] = epistemic
    if add_nature:
        ordered["nature"] = dir_nature

    # ── Serialize and write ──────────────────────────────────────────────────
    yaml_text = serialize_frontmatter(ordered)
    new_content = f"---\n{yaml_text}\n---\n{body}"

    result["action"] = "migrated"
    if not dry_run:
        try:
            filepath.write_text(new_content, encoding="utf-8")
        except OSError as exc:
            result["action"] = "error"
            result["changes"].append(f"cannot write file: {exc}")

    return result


# ═══════════════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════════════

def print_file_result(result: dict, dry_run: bool):
    """Print per-file actions (used with --report)."""
    action = result["action"]
    label = {
        "migrated": "WOULD MIGRATE" if dry_run else "MIGRATED",
        "already-v2": "ALREADY-V2",
        "skipped": "SKIPPED",
        "error": "ERROR",
    }[action]
    print(f"{label:14s} {result['path']}")
    for change in result["changes"]:
        print(f"    + {change}")
    for note in result["review"]:
        print(f"    ! needs-review: {note}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Migrate Acervo frontmatter from v1.0.0 to schema v0.2 (ADR-023).",
    )
    parser.add_argument(
        "--file", metavar="PATH",
        help="Migrate a single markdown file.",
    )
    parser.add_argument(
        "--dir", metavar="PATH",
        help="Migrate all .md files in a directory (recursive; "
             "non-semantic areas excluded, same set as validate_frontmatter.py).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would change without modifying files.",
    )
    parser.add_argument(
        "--report", action="store_true",
        help="Print per-file actions in addition to the summary.",
    )
    args = parser.parse_args(argv)

    if not args.file and not args.dir:
        parser.error("at least one of --file or --dir is required")

    # ── Collect files ──────────────────────────────────────────────────────
    targets = []
    excluded_count = 0

    if args.file:
        file_path = Path(args.file).expanduser().resolve()
        if not file_path.is_file():
            print(f"Error: file not found: {args.file}", file=sys.stderr)
            return 2
        targets.append(file_path)

    if args.dir:
        base = Path(args.dir).expanduser().resolve()
        if not base.is_dir():
            print(f"Error: directory not found: {args.dir}", file=sys.stderr)
            return 2
        for f in sorted(base.rglob("*.md")):
            if is_excluded(f, base):
                excluded_count += 1
            else:
                targets.append(f)

    print("Acervo Frontmatter Migration v1.0.0 → v0.2 (ADR-023)")
    print("=" * 70)
    print(f"Mode:    {'DRY RUN' if args.dry_run else 'MIGRATE'}")
    print(f"Files:   {len(targets)} in scope ({excluded_count} excluded)")
    print()

    # ── Migrate ────────────────────────────────────────────────────────────
    stats = {
        "migrated": 0, "already-v2": 0, "skipped": 0, "error": 0,
        "needs-review": 0,
    }

    for filepath in targets:
        result = migrate_file(filepath, args.dry_run)
        stats[result["action"]] += 1
        if result["review"]:
            stats["needs-review"] += 1
        if args.report:
            print_file_result(result, args.dry_run)
        elif result["review"] or result["action"] == "error":
            # Always surface problems, even without --report.
            print_file_result(result, args.dry_run)

    # ── Summary ────────────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print("Summary:")
    print(f"  Files in scope:  {len(targets)}")
    print(f"  Migrated:        {stats['migrated']}")
    print(f"  Already v0.2:    {stats['already-v2']}")
    print(f"  Needs review:    {stats['needs-review']}")
    print(f"  Skipped:         {stats['skipped']}")
    print(f"  Errors:          {stats['error']}")
    if args.dry_run:
        print()
        print("  (Dry run — no files were modified)")

    return 1 if stats["error"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
