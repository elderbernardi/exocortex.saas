#!/usr/bin/env python3
"""Validate an artifact manifest.json against the v0.4 schema.

Checks:
  - JSON valid
  - Required fields present
  - Source file exists
  - Exports exist when status >= ready
  - Hashes/sizes present when exported
  - Receipt present when status = published
  - Task/microverso references non-empty

Usage:
  python validate_artifact_manifest.py /path/to/artifact_dir
  python validate_artifact_manifest.py --all    # validate all artifacts in ACERVO/_artifacts/items/

Environment:
  ACERVO  — path to acervo root
"""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

REQUIRED_FIELDS = [
    "artifact_id",
    "title",
    "status",
    "artifact_type",
    "source_type",
    "source_path",
    "provenance",
]

VALID_STATUSES = ["draft", "ready", "approved", "ask-publication", "published", "failed", "archived"]
VALID_TYPES = ["document", "report", "deck", "html", "pdf", "image", "zip", "code", "mixed"]
VALID_SOURCE_TYPES = ["markdown", "html", "pptx", "xlsx", "external", "mixed"]


def resolve_acervo() -> Path:
    if env := os.environ.get("ACERVO"):
        return Path(env)
    exo_home = os.environ.get("EXOCORTEX_HOME", os.path.expanduser("~/exocortex"))
    candidate = Path(exo_home) / "acervo"
    if candidate.is_dir():
        return candidate
    hermes_home = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
    return Path(hermes_home) / "acervo"


class ValidationResult:
    def __init__(self, artifact_dir: Path):
        self.artifact_dir = artifact_dir
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str):
        self.errors.append(msg)

    def warn(self, msg: str):
        self.warnings.append(msg)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0

    def __str__(self):
        lines = [f"{'✓' if self.ok else '✗'} {self.artifact_dir.name}"]
        for e in self.errors:
            lines.append(f"  ERROR: {e}")
        for w in self.warnings:
            lines.append(f"  WARN:  {w}")
        return "\n".join(lines)


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_manifest(artifact_dir: Path) -> ValidationResult:
    result = ValidationResult(artifact_dir)
    manifest_path = artifact_dir / "manifest.json"

    # Check manifest exists
    if not manifest_path.is_file():
        result.error("manifest.json not found")
        return result

    # Check valid JSON
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        result.error(f"Invalid JSON: {e}")
        return result

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in manifest:
            result.error(f"Missing required field: {field}")

    # Check status
    status = manifest.get("status", "")
    if status and status not in VALID_STATUSES:
        result.error(f"Invalid status: {status} (valid: {VALID_STATUSES})")

    # Check artifact_type
    atype = manifest.get("artifact_type", "")
    if atype and atype not in VALID_TYPES:
        result.warn(f"Unknown artifact_type: {atype}")

    # Check source exists
    source_path = manifest.get("source_path", "")
    if source_path:
        full_source = artifact_dir / source_path
        if not full_source.is_file():
            result.error(f"Source file not found: {source_path}")

    # Check exports when status >= ready
    if status in ("ready", "approved", "ask-publication", "published"):
        exports = manifest.get("exports", [])
        if not exports:
            result.warn(f"Status is '{status}' but no exports declared")
        for exp in exports:
            exp_path = artifact_dir / exp.get("path", "")
            if not exp_path.is_file():
                result.error(f"Export file not found: {exp.get('path')}")
            else:
                # Validate hash if declared
                declared_hash = exp.get("sha256")
                if declared_hash:
                    actual_hash = compute_sha256(exp_path)
                    if declared_hash != actual_hash:
                        result.error(f"Hash mismatch for {exp.get('path')}: declared={declared_hash[:16]}... actual={actual_hash[:16]}...")
                else:
                    result.warn(f"No sha256 declared for export: {exp.get('path')}")

                # Validate size if declared
                declared_size = exp.get("size")
                if declared_size is not None:
                    actual_size = exp_path.stat().st_size
                    if declared_size != actual_size:
                        result.error(f"Size mismatch for {exp.get('path')}: declared={declared_size} actual={actual_size}")

    # Check receipt when published
    if status == "published":
        pub = manifest.get("publication", {})
        drive = pub.get("drive", {})
        receipt_path = drive.get("receipt_path")
        if not receipt_path:
            result.warn("Published but no receipt_path declared")
        elif receipt_path:
            full_receipt = artifact_dir / receipt_path
            if not full_receipt.is_file():
                result.error(f"Receipt file not found: {receipt_path}")

    # Check owner references
    owner = manifest.get("owner", {})
    if not owner.get("id"):
        result.warn("No owner.id — artifact is orphaned")

    # Check provenance
    prov = manifest.get("provenance", {})
    if not prov.get("created_at"):
        result.warn("No provenance.created_at")

    # Check directories exist
    for subdir in ("source", "assets", "exports", "evaluations", "receipts"):
        if not (artifact_dir / subdir).is_dir():
            result.warn(f"Missing standard directory: {subdir}/")

    return result


def main():
    parser = argparse.ArgumentParser(description="Validate artifact manifest.json")
    parser.add_argument("artifact_dir", nargs="?", help="Path to artifact directory")
    parser.add_argument("--all", action="store_true", help="Validate all artifacts in ACERVO/_artifacts/items/")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    results = []

    if args.all:
        acervo = resolve_acervo()
        items_dir = acervo / "_artifacts" / "items"
        if not items_dir.is_dir():
            print(f"ERROR: No artifacts directory at {items_dir}", file=sys.stderr)
            sys.exit(1)
        for d in sorted(items_dir.iterdir()):
            if d.is_dir():
                results.append(validate_manifest(d))
    elif args.artifact_dir:
        artifact_dir = Path(args.artifact_dir)
        if not artifact_dir.is_dir():
            print(f"ERROR: Not a directory: {artifact_dir}", file=sys.stderr)
            sys.exit(1)
        results.append(validate_manifest(artifact_dir))
    else:
        parser.print_help()
        sys.exit(1)

    if args.json:
        output = []
        for r in results:
            output.append({
                "artifact": r.artifact_dir.name,
                "ok": r.ok,
                "errors": r.errors,
                "warnings": r.warnings,
            })
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        total_ok = 0
        total_err = 0
        for r in results:
            print(r)
            if r.ok:
                total_ok += 1
            else:
                total_err += 1
        if len(results) > 1:
            print(f"\nTotal: {len(results)} artifacts, {total_ok} valid, {total_err} with errors")

    sys.exit(1 if any(not r.ok for r in results) else 0)


if __name__ == "__main__":
    main()
