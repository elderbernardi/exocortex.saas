#!/usr/bin/env python3
"""Validate the Exocórtex conversational dogfood catalog.

The validator keeps the dogfood layer honest:
- every requested EX feature must have a scenario file;
- every scenario must point to a feature declared in FEATURES.md;
- required scenario fields must be present.

It intentionally uses only Python stdlib. Scenario parsing is a minimal YAML subset
sufficient for the repository's dogfood files: scalar keys, literal blocks and
simple dash lists.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

FEATURE_RE = re.compile(r"\bEX-(\d{2})\b")
REQUIRED_SCENARIO_FIELDS = [
    "feature_id",
    "title",
    "category",
    "source",
    "risk",
    "mode",
    "user_prompt",
    "success_criteria",
    "failure_signals",
    "evidence_required",
]


@dataclass
class CatalogValidationResult:
    ok: bool
    feature_ids: list[str] = field(default_factory=list)
    scenario_ids: list[str] = field(default_factory=list)
    missing_scenarios: list[str] = field(default_factory=list)
    orphan_scenarios: list[str] = field(default_factory=list)
    invalid_scenarios: dict[str, list[str]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


def extract_feature_ids(text: str) -> list[str]:
    """Return unique EX feature IDs in document order."""
    seen: set[str] = set()
    ordered: list[str] = []
    for match in FEATURE_RE.finditer(text):
        feature_id = f"EX-{match.group(1)}"
        if feature_id not in seen:
            seen.add(feature_id)
            ordered.append(feature_id)
    return ordered


def parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse the minimal YAML subset used by dogfood scenarios."""
    data: dict[str, Any] = {}
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        if ":" not in raw:
            i += 1
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value == "|":
            block: list[str] = []
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if nxt and not nxt.startswith((" ", "\t")) and ":" in nxt:
                    break
                block.append(nxt[2:] if nxt.startswith("  ") else nxt.lstrip())
                i += 1
            data[key] = "\n".join(block).rstrip()
            continue
        if value == "":
            items: list[str] = []
            i += 1
            while i < len(lines):
                nxt = lines[i]
                stripped_next = nxt.strip()
                if not stripped_next:
                    i += 1
                    continue
                if stripped_next.startswith("- "):
                    items.append(stripped_next[2:].strip())
                    i += 1
                    continue
                if not nxt.startswith((" ", "\t")) and ":" in nxt:
                    break
                i += 1
            data[key] = items
            continue
        data[key] = value.strip('"\'')
        i += 1
    return data


def validate_scenario_file(path: Path) -> tuple[str | None, list[str]]:
    errors: list[str] = []
    try:
        scenario = parse_simple_yaml(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return None, [f"cannot read scenario: {exc}"]

    feature_id = scenario.get("feature_id")
    if not feature_id:
        errors.append("missing field: feature_id")
    elif not re.fullmatch(r"EX-\d{2}", str(feature_id)):
        errors.append(f"invalid feature_id: {feature_id}")

    for field_name in REQUIRED_SCENARIO_FIELDS:
        value = scenario.get(field_name)
        if value in (None, "", []):
            errors.append(f"missing field: {field_name}")

    return str(feature_id) if feature_id else None, errors


def validate_catalog(
    root: Path,
    required_ids: list[str] | None = None,
    allow_missing: bool = False,
) -> CatalogValidationResult:
    features_path = root / "FEATURES.md"
    scenario_dir = root / ".dogfood" / "scenarios"
    errors: list[str] = []

    if not features_path.is_file():
        errors.append(f"FEATURES.md not found: {features_path}")
        return CatalogValidationResult(ok=False, errors=errors)

    feature_ids = extract_feature_ids(features_path.read_text(encoding="utf-8"))
    if required_ids:
        feature_ids = [fid for fid in feature_ids if fid in required_ids]

    if not scenario_dir.is_dir():
        errors.append(f"scenario dir not found: {scenario_dir}")
        scenario_ids: list[str] = []
        invalid: dict[str, list[str]] = {}
    else:
        scenario_ids = []
        invalid = {}
        for path in sorted(scenario_dir.glob("EX-*.yaml")):
            scenario_id, scenario_errors = validate_scenario_file(path)
            scenario_id = scenario_id or path.stem
            if required_ids and scenario_id not in required_ids:
                continue
            scenario_ids.append(scenario_id)
            if scenario_errors:
                invalid[scenario_id] = scenario_errors

    feature_set = set(feature_ids)
    scenario_set = set(scenario_ids)
    missing = sorted(feature_set - scenario_set)
    orphan = sorted(scenario_set - set(extract_feature_ids(features_path.read_text(encoding="utf-8"))))

    if missing and not allow_missing:
        errors.append("missing scenarios: " + ", ".join(missing))
    if orphan:
        errors.append("orphan scenarios: " + ", ".join(orphan))
    for scenario_id, scenario_errors in invalid.items():
        errors.append(f"invalid {scenario_id}: " + "; ".join(scenario_errors))

    return CatalogValidationResult(
        ok=not errors,
        feature_ids=feature_ids,
        scenario_ids=sorted(scenario_ids),
        missing_scenarios=missing,
        orphan_scenarios=orphan,
        invalid_scenarios=invalid,
        errors=errors,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--allow-missing", action="store_true", help="report missing scenarios without failing")
    parser.add_argument("--required", nargs="*", help="only validate these feature IDs")
    args = parser.parse_args(argv)

    result = validate_catalog(Path(args.root), required_ids=args.required, allow_missing=args.allow_missing)
    print(f"features={len(result.feature_ids)} scenarios={len(result.scenario_ids)}")
    if result.missing_scenarios:
        print("missing=" + ",".join(result.missing_scenarios))
    if result.orphan_scenarios:
        print("orphan=" + ",".join(result.orphan_scenarios))
    for error in result.errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
