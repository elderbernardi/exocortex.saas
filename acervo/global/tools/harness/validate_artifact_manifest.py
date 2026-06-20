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


def check_antislop(content: str) -> tuple[int, list[str]]:
    """Evaluate text content against anti-slop rules.
    Returns (score, list of issues found).
    """
    import re
    issues = []
    score = 50

    # 1. Buzzwords / AI-slop words (Portuguese and English)
    slop_patterns = {
        r"\bcrucial\b": 3,
        r"\btapestry\b": 3,
        r"\bdelve\b": 3,
        r"\btestament\b": 3,
        r"\bmoreover\b": 3,
        r"\bfurthermore\b": 3,
        r"\btapestria\b": 3,
        r"\btestamento\b": 3,
        r"\balém disso\b": 3,
        r"\bimportante notar\b": 3,
        r"\bimportante ressaltar\b": 3,
        r"\bcabe destacar\b": 3,
        r"\bsignificativamente\b": 3,
        r"\bcom o objetivo de\b": 2,
        r"\ba fim de\b": 2,
    }
    
    for pattern, penalty in slop_patterns.items():
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            count = len(matches)
            term = pattern.strip("\\b")
            issues.append(f"AI-slop term '{term}' found {count} time(s)")
            score -= penalty * count

    # 2. Adverbs ending in "-mente" in Portuguese
    adverbs = re.findall(r"\b\w+mente\b", content, re.IGNORECASE)
    words = content.split()
    word_count = len(words)
    if word_count > 0:
        adverb_ratio = len(adverbs) / word_count
        if adverb_ratio > 0.01:
            excess = len(adverbs) - int(word_count * 0.01)
            issues.append(f"Excessive adverbs ({len(adverbs)} found, ratio {adverb_ratio:.2%})")
            score -= excess * 1

    # 3. Passive voice markers in Portuguese
    passive_voice_regex = r"\b(foi|foram|será|serão|seria|seriam|tinha sido|tinham sido)\b\s+\w+ad[oa]s?\b"
    passive_matches = re.findall(passive_voice_regex, content, re.IGNORECASE)
    if passive_matches:
        count = len(passive_matches)
        issues.append(f"Passive voice pattern found {count} time(s)")
        score -= count * 2

    # 4. Em-dashes
    em_dashes = re.findall(r"[—–]", content)
    if em_dashes:
        count = len(em_dashes)
        issues.append(f"Em-dash ('—') found {count} time(s)")
        score -= count * 2

    score = max(0, min(50, score))
    return score, issues


def check_taste(content: str) -> list[str]:
    """Evaluate HTML content against visual taste rules.
    Returns list of issues found.
    """
    import re
    issues = []

    # 1. Meta-labels genéricos
    meta_patterns = [
        r"\bSECTION \d+\b",
        r"\bSECTION_\d+\b",
        r"\bSECTION\d+\b",
        r"\bTEMPLATE\b",
        r"\bOPTION [A-Z]\b",
        r"\bPLACEHOLDER\b",
    ]
    for pattern in meta_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            label = pattern.strip("\\b")
            issues.append(f"Meta-label/placeholder '{label}' found")

    # 2. Empty grids
    empty_grid = re.search(r'<div[^>]*class="[^"]*grid[^"]*"[^>]*>\s*</div>', content, re.IGNORECASE)
    if empty_grid:
        issues.append("Empty grid container found")

    return issues


def validate_quality(artifact_dir: Path, manifest: dict, result: ValidationResult):
    status = manifest.get("status", "draft")
    is_draft = (status == "draft")

    artifact_type = manifest.get("artifact_type", "")
    source_type = manifest.get("source_type", "")

    # A) Check prose quality (anti-slop)
    is_textual = (source_type == "markdown") or (artifact_type in ("document", "report"))
    if is_textual:
        source_path = manifest.get("source_path", "source/source.md")
        full_source = artifact_dir / source_path
        if full_source.is_file():
            try:
                content = full_source.read_text(encoding="utf-8")
                score, issues = check_antislop(content)
                if score < 35:
                    msg = f"Anti-slop quality check failed (score: {score}/50, minimum: 35/50). Issues: {', '.join(issues)}"
                    if is_draft:
                        result.warn(msg)
                    else:
                        result.error(msg)
            except Exception as e:
                result.warn(f"Failed to read/evaluate source for quality: {e}")

    # B) Check visual taste
    is_visual = (artifact_type in ("deck", "html")) or (source_type == "html")
    html_files = []
    if is_visual:
        for exp in manifest.get("exports", []):
            path_str = exp.get("path", "")
            if path_str.endswith(".html"):
                html_files.append(artifact_dir / path_str)
        # Also check source if HTML
        if source_type == "html" and (source_path := manifest.get("source_path")):
            html_files.append(artifact_dir / source_path)

    for html_file in html_files:
        if html_file.is_file():
            try:
                content = html_file.read_text(encoding="utf-8")
                issues = check_taste(content)
                if issues:
                    msg = f"Visual taste check failed in {html_file.name}. Issues: {', '.join(issues)}"
                    if is_draft:
                        result.warn(msg)
                    else:
                        result.error(msg)
            except Exception as e:
                result.warn(f"Failed to read/evaluate HTML {html_file.name} for taste: {e}")


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

    # Validate quality (anti-slop and visual taste)
    validate_quality(artifact_dir, manifest, result)

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
        skipped_non_artifacts = []
        for d in sorted(items_dir.iterdir()):
            if not d.is_dir():
                continue
            # Only validate genuine artifact packages: a dir is an artifact iff it
            # carries a manifest.json or follows the art_* id convention. Other
            # dirs under items/ (e.g. patches/, repairs/) are not artifacts and
            # would otherwise fail spuriously with "manifest.json not found".
            if (d / "manifest.json").is_file() or d.name.startswith("art_"):
                results.append(validate_manifest(d))
            else:
                skipped_non_artifacts.append(d.name)
        if skipped_non_artifacts and not args.json:
            print(f"# Skipped {len(skipped_non_artifacts)} non-artifact dir(s) under items/: "
                  f"{', '.join(skipped_non_artifacts)}")
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
