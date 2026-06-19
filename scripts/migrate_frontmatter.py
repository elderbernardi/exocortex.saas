#!/usr/bin/env python3
"""
migrate_frontmatter.py — Migrate Acervo frontmatter to OKF-aligned schema (ADR-013)

Reads existing YAML frontmatter from Acervo markdown files and adds the new
OKF canonical fields (type, title, description, tags, timestamp) and Acervo
extension fields (class, created_at, last_accessed_at). Renames the legacy
`type` field to `excrtx_type` to avoid collision with the new OKF `type`.

Implements the migration rules defined in:
  - schema-spec.md Section 3 (Field Mapping + Derivation Logic)
  - ADR-013 (Frontmatter Schema with OKF v0.1 Alignment)
  - tasks/08-migrate-canonical-microversos.md

Usage:
    python3 scripts/migrate_frontmatter.py --dry-run --dir ~/.hermes/acervo --verbose
    python3 scripts/migrate_frontmatter.py --dir ~/.hermes/acervo

Exit codes:
    0 — migration completed (or dry-run completed) with no errors
    1 — one or more files had errors during migration
    2 — target directory not found
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required. Install with: pip install pyyaml")

try:
    from dateutil import parser as dateutil_parser
    _HAS_DATEUTIL = True
except ImportError:
    _HAS_DATEUTIL = False


# ═══════════════════════════════════════════════════════════════════════════
#  YAML Loader / Dumper
# ═══════════════════════════════════════════════════════════════════════════

class FrontmatterLoader(yaml.SafeLoader):
    """SafeLoader variant that does not auto-parse dates/timestamps.

    Without this, PyYAML converts ``created: 2026-06-11`` into a
    ``datetime.date`` object. We need the raw string so format validation
    and derivation logic can inspect the exact textual representation.
    """


# Remove the timestamp implicit resolver so dates stay as plain strings.
_clean_resolvers = {}
for _ch, _resolvers in list(yaml.SafeLoader.yaml_implicit_resolvers.items()):
    _clean_resolvers[_ch] = [
        (tag, regexp) for tag, regexp in _resolvers
        if tag != "tag:yaml.org,2002:timestamp"
    ]
FrontmatterLoader.yaml_implicit_resolvers = _clean_resolvers


class FrontmatterDumper(yaml.SafeDumper):
    """Dumper that uses flow-style for simple scalar lists.

    This keeps tags and similar short lists on a single line
    (``tags: [a, b, c]``) while block-formatting nested structures.
    """


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

# Remove the timestamp implicit resolver from the Dumper as well, so that
# date-like strings (e.g. "2026-06-11") are not needlessly quoted in output.
_dumper_resolvers = {}
for _ch, _resolvers in list(yaml.SafeDumper.yaml_implicit_resolvers.items()):
    _dumper_resolvers[_ch] = [
        (tag, regexp) for tag, regexp in _resolvers
        if tag != "tag:yaml.org,2002:timestamp"
    ]
FrontmatterDumper.yaml_implicit_resolvers = _dumper_resolvers


# ═══════════════════════════════════════════════════════════════════════════
#  Constants — Migration Tables (from schema-spec.md §3)
# ═══════════════════════════════════════════════════════════════════════════

# Directories excluded from migration entirely.
EXCLUDED_DIRS = frozenset({
    "macro", "raw", "_archive", "_inbox", "_artifacts",
    "_template", ".quarantine",
})

# ─── OKF type derivation: directory name → OKF concept type ─────────────────
# Source: schema-spec.md §3.2, table "Directory Path Pattern → OKF type"
DIR_TYPE_MAP = {
    "decisions": "decision",
    "knowledge": "knowledge",
    "reflections": "reflection",
    "context": "context",
    "memories": "memory",
    "workflows": "artifact",
    "tools": "artifact",
    "contracts": "decision",       # binding decisions/standards
    "persona": "context",
    "prompts": "artifact",
    "skills": "artifact",
    "templates": "artifact",
    "raw": "knowledge",
    "_meta": "context",
}

# ─── OKF type derivation: nature value → OKF concept type ───────────────────
# Includes both English and Portuguese nature values.
# Source: schema-spec.md §3.2, tables "nature value → OKF type"
NATURE_TYPE_MAP = {
    # English
    "decisions": "decision",
    "knowledge": "knowledge",
    "context": "context",
    "reflections": "reflection",
    "contracts": "decision",
    "tools": "artifact",
    "workflows": "artifact",
    "templates": "artifact",
    "persona": "context",
    "prompts": "artifact",
    "skills": "artifact",
    "meta": "context",
    # Portuguese
    "conhecimento": "knowledge",
    "contexto": "context",
    "reflexoes": "reflection",
    "processos": "artifact",       # = workflows
    "ferramentas": "artifact",     # = tools
    "instrucoes": "decision",      # = contracts
}

# ─── class derivation: directories that default to `perene` ─────────────────
# Source: schema-spec.md §3.3, table "Directory Path Pattern → Default class"
DIR_CLASS_PERENE = frozenset({
    "decisions", "reflections", "contracts", "persona", "_meta",
})

# Filenames that default to `perene` regardless of directory.
PERENE_FILENAMES = frozenset({
    "index.md", "log.md", "_seed.md", "SCHEMA.md", "DESIGN.md",
})

# Filenames that default OKF type to `context`.
CONTEXT_FILENAMES = frozenset({
    "index.md", "log.md", "_seed.md",
})

# Valid OKF concept types.
ALLOWED_TYPES = frozenset({
    "decision", "memory", "reflection", "context", "knowledge", "artifact",
})


# ═══════════════════════════════════════════════════════════════════════════
#  Path / Scope Helpers
# ═══════════════════════════════════════════════════════════════════════════

def is_excluded(path: Path, base: Path) -> bool:
    """True if *path* lives inside an excluded directory relative to *base*."""
    try:
        rel = path.relative_to(base)
    except ValueError:
        return True
    for part in rel.parts:
        if part in EXCLUDED_DIRS:
            return True
    return False


def relative_path(path: Path, base: Path) -> Path:
    """Return *path* relative to *base*, falling back to *path* itself."""
    try:
        return path.relative_to(base)
    except ValueError:
        return path


def find_nature_dir(rel_path: Path) -> str | None:
    """Find the nature directory (e.g. ``decisions``, ``knowledge``) in *rel_path*.

    Scans path parts from leaf upward and returns the first component that
    appears in ``DIR_TYPE_MAP``.
    """
    for part in reversed(rel_path.parts[:-1]):  # skip filename
        if part in DIR_TYPE_MAP:
            return part
    return None


# ═══════════════════════════════════════════════════════════════════════════
#  Derivation Logic
# ═══════════════════════════════════════════════════════════════════════════

def derive_type(rel_path: Path, nature: str | None) -> str:
    """Derive OKF ``type`` (concept type) from directory → nature → default.

    Priority: directory path → nature value → default (``knowledge``).
    Source: schema-spec.md §3.2.
    """
    filename = rel_path.name
    if filename in CONTEXT_FILENAMES:
        return "context"

    nature_dir = find_nature_dir(rel_path)
    if nature_dir and nature_dir in DIR_TYPE_MAP:
        return DIR_TYPE_MAP[nature_dir]

    if nature and nature in NATURE_TYPE_MAP:
        return NATURE_TYPE_MAP[nature]

    return "knowledge"


def derive_class(rel_path: Path, existing_class: str | None) -> str:
    """Derive lifecycle ``class`` from directory path or special filenames.

    If *existing_class* is already set (and valid), respect it.
    Source: schema-spec.md §3.3.
    """
    if existing_class and existing_class in ("perene", "volátil"):
        return existing_class

    if rel_path.name in PERENE_FILENAMES:
        return "perene"

    for part in rel_path.parts:
        if part in DIR_CLASS_PERENE:
            return "perene"

    return "volátil"


def derive_title(data: dict, body: str, filepath: Path) -> str:
    """Derive ``title`` from existing field → H1 heading → filename."""
    existing = data.get("title")
    if isinstance(existing, str) and existing.strip():
        return existing.strip()

    # First H1 heading in body
    for line in body.split("\n"):
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()

    # Filename (without extension)
    return filepath.stem


def derive_description(data: dict, body: str, title: str) -> str:
    """Derive ``description`` from existing field → first body line → title.

    Source: schema-spec.md §3.3 "description Default Derivation".
    """
    existing = data.get("description")
    if isinstance(existing, str) and existing.strip():
        return existing.strip()

    for line in body.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        # Strip leading blockquote / list markers
        if stripped.startswith(">"):
            stripped = stripped[1:].lstrip()
        elif stripped.startswith("- "):
            stripped = stripped[2:].lstrip()
        if not stripped:
            continue
        # Truncate to 120 chars with ellipsis
        if len(stripped) > 120:
            return stripped[:117] + "..."
        return stripped

    # Fallback: use title
    return title


def normalize_tags(tags) -> list:
    """Normalize ``tags`` to a list.

    - ``None`` → ``[]``
    - string → ``[string]``  (edge case from schema-spec §3.5)
    - list → as-is
    """
    if tags is None:
        return []
    if isinstance(tags, list):
        return tags
    if isinstance(tags, str):
        return [tags]
    return []


# ═══════════════════════════════════════════════════════════════════════════
#  Timestamp Derivation
# ═══════════════════════════════════════════════════════════════════════════

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def parse_created(value) -> tuple[str | None, str | None]:
    """Parse a ``created`` field value into ``(timestamp, created_at)``.

    Returns ``(date_str, datetime_str)`` or ``(None, None)`` if unparseable.

    Handles:
      - ``YYYY-MM-DD`` → timestamp = date; created_at = date + T00:00:00Z
      - ``YYYY-MM-DDTHH:MM:SSZ`` → split accordingly
      - Other formats via dateutil (if available), normalized to UTC
    """
    if value is None:
        return None, None

    if not isinstance(value, str):
        value = str(value)

    value = value.strip()
    if not value:
        return None, None

    # Pure date: YYYY-MM-DD
    if _DATE_RE.match(value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value, f"{value}T00:00:00Z"
        except ValueError:
            pass

    # Full UTC datetime: YYYY-MM-DDTHH:MM:SSZ
    if _DATETIME_RE.match(value):
        try:
            datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
            return value[:10], value
        except ValueError:
            pass

    # Try dateutil for non-standard formats
    if _HAS_DATEUTIL:
        try:
            dt = dateutil_parser.parse(value)
            if dt.tzinfo is not None:
                dt = dt.astimezone(timezone.utc)
            else:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.strftime("%Y-%m-%d"), dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            pass

    return None, None


def git_first_commit_date(filepath: Path) -> tuple[str | None, str | None]:
    """Try to get the first-commit author date from git.

    Returns ``(timestamp, created_at)`` or ``(None, None)`` if not in a git
    repo or git is unavailable.
    """
    if not shutil.which("git"):
        return None, None

    try:
        result = subprocess.run(
            [
                "git", "log", "--diff-filter=A", "--follow",
                "--format=%aI", "--", str(filepath),
            ],
            capture_output=True, text=True, timeout=10,
            cwd=str(filepath.parent) if filepath.parent.exists() else None,
        )
    except Exception:
        return None, None

    if result.returncode != 0 or not result.stdout.strip():
        return None, None

    # Take the oldest (last line) if multiple Add events
    lines = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
    if not lines:
        return None, None

    iso_str = lines[-1]

    # Try dateutil to normalize timezone to UTC
    if _HAS_DATEUTIL:
        try:
            dt = dateutil_parser.parse(iso_str)
            if dt.tzinfo is not None:
                dt = dt.astimezone(timezone.utc)
            else:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.strftime("%Y-%m-%d"), dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception:
            pass

    return None, None


def file_mtime(filepath: Path) -> tuple[str, str]:
    """Return ``(timestamp, created_at)`` from file modification time."""
    mtime = filepath.stat().st_mtime
    dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d"), dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def derive_timestamps(data: dict, filepath: Path) -> tuple[str, str, list[str]]:
    """Derive ``timestamp`` and ``created_at``.

    Fallback chain (schema-spec §3.4):
      1. ``created`` field
      2. git log (first add)
      3. file mtime
      4. current UTC datetime (last resort)

    Returns ``(timestamp, created_at, warnings)``.
    """
    warnings = []

    # 1. Try `created` field
    created_value = data.get("created")
    timestamp, created_at = parse_created(created_value)
    if timestamp:
        return timestamp, created_at, warnings

    if created_value is not None:
        warnings.append(
            f"Could not parse 'created' value {repr(created_value)}; "
            f"falling back to git/mtime"
        )

    # 2. Try git log
    timestamp, created_at = git_first_commit_date(filepath)
    if timestamp:
        return timestamp, created_at, warnings

    # 3. Try file mtime
    timestamp, created_at = file_mtime(filepath)
    warnings.append(f"Used file mtime as fallback: {timestamp}")
    return timestamp, created_at, warnings


# ═══════════════════════════════════════════════════════════════════════════
#  Frontmatter Extraction & Serialization
# ═══════════════════════════════════════════════════════════════════════════

def extract_frontmatter(text: str) -> tuple[dict | None, str, bool]:
    """Extract frontmatter and body from markdown text.

    Returns ``(data, body, had_frontmatter)``.
    If the file has no frontmatter, returns ``(None, text, False)``.
    """
    lines = text.split("\n")

    if not lines or lines[0].rstrip("\r") != "---":
        return None, text, False

    # Find closing ---
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

# Fields that are consumed during migration (not retained in output).
CONSUMED_FIELDS = frozenset({"created"})

# New fields added by the migration.
NEW_FIELDS_ORDER = [
    # OKF Canonical
    "type", "title", "description", "tags", "timestamp",
    # Acervo Extension
    "class", "created_at", "last_accessed_at", "promoted_at",
]


def migrate_file(
    filepath: Path,
    base: Path,
    dry_run: bool,
    verbose: bool,
) -> dict:
    """Migrate a single markdown file.

    Returns a result dict with keys:
      ``path``, ``action`` (modified|unchanged|error),
      ``changes`` (list[str]), ``warnings`` (list[str]).
    """
    result = {
        "path": str(filepath),
        "action": "skip",
        "changes": [],
        "warnings": [],
    }

    try:
        original_text = filepath.read_text(encoding="utf-8")
    except OSError as exc:
        result["action"] = "error"
        result["warnings"].append(f"Cannot read file: {exc}")
        return result

    data, body, had_fm = extract_frontmatter(original_text)
    if data is None:
        data = {}

    rel = relative_path(filepath, base)

    # ── Save original key order for legacy field preservation ──────────────
    original_keys = list(data.keys())

    # ── Step 1: Rename legacy `type` → `excrtx_type` ───────────────────────
    # Critical: do this BEFORE adding the new OKF `type` to avoid collision.
    old_type = data.pop("type", None)
    if old_type is not None:
        # Only set excrtx_type if it doesn't already exist (idempotency).
        if "excrtx_type" not in data:
            data["excrtx_type"] = old_type
            result["changes"].append(f"renamed type→excrtx_type: {old_type!r}")
        else:
            result["warnings"].append(
                f"Both 'type' and 'excrtx_type' present; "
                f"kept existing excrtx_type={data['excrtx_type']!r}, "
                f"discarded old type={old_type!r}"
            )

    # ── Step 2: Derive OKF canonical fields ────────────────────────────────
    nature = data.get("nature")
    nature_str = nature if isinstance(nature, str) else None

    # type (OKF concept type — always set)
    new_type = derive_type(rel, nature_str)
    data["type"] = new_type
    result["changes"].append(f"type: {new_type}")

    # title
    new_title = derive_title(data, body, filepath)
    data["title"] = new_title
    result["changes"].append(f"title: {new_title!r}")

    # description
    new_desc = derive_description(data, body, new_title)
    data["description"] = new_desc
    result["changes"].append(
        f"description: {new_desc[:60]!r}{'...' if len(new_desc) > 60 else ''}"
    )

    # tags
    tags = normalize_tags(data.get("tags"))
    data["tags"] = tags
    result["changes"].append(f"tags: {tags}")

    # timestamp + created_at
    timestamp, created_at, ts_warnings = derive_timestamps(data, filepath)
    data["timestamp"] = timestamp
    data["created_at"] = created_at
    result["changes"].append(f"timestamp: {timestamp}")
    result["changes"].append(f"created_at: {created_at}")
    result["warnings"].extend(ts_warnings)

    # ── Step 3: Add Acervo extension fields ────────────────────────────────
    # class — respect existing value if valid
    existing_class = data.get("class")
    new_class = derive_class(rel, existing_class)
    data["class"] = new_class
    result["changes"].append(f"class: {new_class}")

    # last_accessed_at — set to created_at value (per Task 08 spec)
    data["last_accessed_at"] = created_at
    result["changes"].append(f"last_accessed_at: {created_at}")

    # promoted_at — leave empty (only set on explicit promotion; do NOT add)

    # ── Step 4: Build ordered output ───────────────────────────────────────
    # Order: OKF canonical → Acervo extension → legacy retained (original order)
    ordered = {}

    # New fields in canonical order
    for key in NEW_FIELDS_ORDER:
        if key in data and key != "promoted_at":  # don't add promoted_at
            ordered[key] = data[key]

    # Legacy fields — preserve original insertion order
    for key in original_keys:
        if key in CONSUMED_FIELDS:
            continue  # `created` is consumed
        if key == "type":
            continue  # already renamed to excrtx_type
        if key in ordered:
            continue  # already placed (title, tags, description, class, etc.)
        ordered[key] = data[key]

    # excrtx_type — place right after the new fields, before other legacy
    # (it was popped from original_keys as "type", so add it here)
    if "excrtx_type" in data and "excrtx_type" not in ordered:
        # Insert after Acervo extension fields
        insert_pos = len(NEW_FIELDS_ORDER)
        items = list(ordered.items())
        items.insert(insert_pos, ("excrtx_type", data["excrtx_type"]))
        ordered = dict(items)

    # Any remaining fields not yet placed
    for key, value in data.items():
        if key not in ordered:
            ordered[key] = value

    # ── Step 5: Serialize and write ────────────────────────────────────────
    yaml_text = serialize_frontmatter(ordered)

    if had_fm:
        new_content = f"---\n{yaml_text}\n---\n{body}"
    else:
        # No previous frontmatter — create new block
        body_clean = body.lstrip("\n")
        new_content = f"---\n{yaml_text}\n---\n\n{body_clean}"

    # Check if content actually changed
    if new_content == original_text:
        result["action"] = "unchanged"
        if verbose:
            print(f"UNCHANGED: {filepath}")
    else:
        result["action"] = "modified"
        if dry_run:
            if verbose:
                print(f"\n{'─' * 70}")
                print(f"WOULD MODIFY: {filepath}")
                if not had_fm:
                    print("  (no previous frontmatter — creating new)")
                for change in result["changes"]:
                    print(f"  + {change}")
                for warning in result["warnings"]:
                    print(f"  ! {warning}")
                yaml_lines = yaml_text.split("\n")
                print(f"  New frontmatter preview:")
                for line in yaml_lines[:20]:
                    print(f"    {line}")
                if len(yaml_lines) > 20:
                    extra = len(yaml_lines) - 20
                    print(f"    ... ({extra} more lines)")
        else:
            filepath.write_text(new_content, encoding="utf-8")
            if verbose:
                print(f"MODIFIED: {filepath}")
                for change in result["changes"]:
                    print(f"  + {change}")
                for warning in result["warnings"]:
                    print(f"  ! {warning}")

    return result


# ═══════════════════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════════════════

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Migrate Acervo frontmatter to OKF-aligned schema (ADR-013).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would change without modifying files.",
    )
    parser.add_argument(
        "--dir", metavar="PATH",
        default=os.environ.get(
            "ACERVO", str(Path.home() / ".hermes" / "acervo")
        ),
        help="Target directory (default: $ACERVO or ~/.hermes/acervo).",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Show per-file changes.",
    )
    args = parser.parse_args(argv)

    base = Path(args.dir).expanduser().resolve()
    if not base.is_dir():
        print(f"Error: directory not found: {args.dir}", file=sys.stderr)
        return 2

    # ── Collect files ──────────────────────────────────────────────────────
    all_files = sorted(base.rglob("*.md"))

    in_scope = []
    excluded_count = 0
    for f in all_files:
        if is_excluded(f, base):
            excluded_count += 1
        else:
            in_scope.append(f)

    print("Acervo Frontmatter Migration (ADR-013)")
    print("=" * 70)
    print(f"Target:  {base}")
    print(f"Mode:    {'DRY RUN' if args.dry_run else 'MIGRATE'}")
    print(f"Files:   {len(all_files)} total "
          f"({len(in_scope)} in scope, {excluded_count} excluded)")
    print()

    # ── Migrate ────────────────────────────────────────────────────────────
    stats = {"modified": 0, "unchanged": 0, "errors": 0, "warnings": 0}

    for filepath in in_scope:
        result = migrate_file(filepath, base, args.dry_run, args.verbose)

        if result["action"] == "modified":
            stats["modified"] += 1
        elif result["action"] == "unchanged":
            stats["unchanged"] += 1
        elif result["action"] == "error":
            stats["errors"] += 1

        if result["warnings"]:
            stats["warnings"] += 1

    # ── Summary ────────────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print("Summary:")
    print(f"  Files in scope:     {len(in_scope)}")
    print(f"  Modified:           {stats['modified']}")
    print(f"  Already compliant:  {stats['unchanged']}")
    print(f"  Errors:             {stats['errors']}")
    print(f"  Files w/ warnings:  {stats['warnings']}")
    if args.dry_run:
        print()
        print("  (Dry run — no files were modified)")

    return 1 if stats["errors"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
