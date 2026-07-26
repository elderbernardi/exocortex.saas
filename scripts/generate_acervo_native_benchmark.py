#!/usr/bin/env python3
"""Generate the preregistered deterministic Acervo-native evaluation suite."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def session(session_id: str, microverse: str, text: str, **metadata: Any) -> dict[str, Any]:
    return {
        "session_id": session_id, "microverse": microverse,
        "date": metadata.pop("date", "2026-01-01"),
        "turns": [{"role": "user", "content": text}], **metadata,
    }


def generate() -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    # 400 forbidden-scope traps. Both scopes carry the same rare marker, so only
    # scope enforcement—not lexical luck—can prevent the forbidden hit.
    for i in range(400):
        marker = f"isolationmarker{i:04d}x"
        home, foreign = f"home-{i:04d}", f"foreign-{i:04d}"
        target, forbidden = f"target-{i:04d}", f"forbidden-{i:04d}"
        cases.append({
            "case_id": f"isolation-{i:04d}", "ability": "cross-scope-trap", "scope": home,
            "question": f"What is the approved value for {marker}?",
            "sessions": [
                session(target, home, f"The approved {marker} value is HOME-CORRECT-{i:04d}."),
                session(forbidden, foreign, f"The approved {marker} value is FOREIGN-SECRET-{i:04d}.", sensitivity="restricted"),
            ],
            "expected_session_ids": [target], "forbidden_session_ids": [forbidden],
        })
    # 100 explicitly authorized cross-scope reads. These are internal, never restricted.
    for i in range(100):
        marker = f"bridgemarker{i:04d}x"
        home, remote = f"bridge-home-{i:04d}", f"bridge-remote-{i:04d}"
        target = f"bridge-target-{i:04d}"
        cases.append({
            "case_id": f"bridge-{i:04d}", "ability": "cross-scope-allowed", "scope": home,
            "allow_scopes": [remote], "question": f"Find the authorized {marker} record.",
            "sessions": [session(target, remote, f"Authorized {marker} record is BRIDGE-{i:04d}.")],
            "expected_session_ids": [target],
        })
    # Active/superseded chains test that current questions do not return stale facts.
    for i in range(100):
        marker, scope = f"temporalmarker{i:04d}x", f"temporal-{i:04d}"
        old, active = f"old-{i:04d}", f"active-{i:04d}"
        cases.append({
            "case_id": f"temporal-{i:04d}", "ability": "knowledge-update", "scope": scope,
            "question": f"What is the current value for {marker}?", "question_date": "2026-06-01",
            "sessions": [
                session(old, scope, f"The {marker} value was OLD-{i:04d}.", status="superseded", date="2025-01-01"),
                session(active, scope, f"The current {marker} value is ACTIVE-{i:04d}.", date="2026-05-01"),
            ],
            "expected_session_ids": [active], "forbidden_session_ids": [old],
        })
    # Consolidation extraction ground truth: full adapters must expose the types
    # of retrieved consolidated objects in extracted_object_types.
    for i in range(100):
        marker, scope = f"extractionmarker{i:04d}x", f"extract-{i:04d}"
        source = f"extract-source-{i:04d}"
        cases.append({
            "case_id": f"extraction-{i:04d}", "ability": "consolidation-extraction", "scope": scope,
            "question": f"Who owns the commitment described by {marker}?",
            "sessions": [session(source, scope, f"At {marker}, entity Ana promised to deliver the report on Friday.")],
            "expected_session_ids": [source], "expected_object_types": ["episode", "entity", "intention"],
        })
    # 100 absent/adversarial questions measure explicit abstention.
    for i in range(100):
        scope = f"absent-{i:04d}"
        cases.append({
            "case_id": f"absent-{i:04d}", "ability": "abstention", "scope": scope,
            "question": f"What is the nonexistent adversarialmarker{i:04d}x contract?",
            "sessions": [session(f"noise-{i:04d}", scope, "This session contains ordinary unrelated notes.")],
            "expected_session_ids": [], "expects_abstention": True,
        })
    return {
        "schema_version": "1.0", "seed": 20260713,
        "counts": {
            "cross_scope_trap": 400, "cross_scope_allowed": 100,
            "knowledge_update": 100, "consolidation_extraction": 100, "abstention": 100,
        },
        "cases": cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(generate(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "n": len(generate()["cases"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
