#!/usr/bin/env python3
"""
auditor_pipeline.py — Exocórtex Auditor Pipeline Orchestrator

Runs 3-phase post-hoc audit on agent output:
  Phase 1: Structural (tool trace — Draft-First, accuracy, tool governance)
  Phase 2: Anti-Slop (regex content scoring — PT + EN patterns)
  Phase 3: Canvas (structured output validation)

Usage:
    python3 auditor_pipeline.py --transcript <path> --trace <path>
    python3 auditor_pipeline.py --transcript <path> --trace <path> --json
"""

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

# Import phase auditors
sys.path.insert(0, str(Path(__file__).parent))
from auditor_structural import check_structural
from auditor_antislop import extract_prose, score_text
from auditor_canvas_validator import validate_canvas


@dataclass
class PipelineResult:
    passed: bool
    structural: dict = field(default_factory=dict)
    antislop: dict = field(default_factory=dict)
    canvas: dict = field(default_factory=dict)
    summary: str = ""

    def to_dict(self):
        return asdict(self)


def audit(transcript_path: Path, tool_trace_path: Path) -> PipelineResult:
    """Run 3-phase audit on agent output."""

    # Phase 1: Structural (tool trace)
    if tool_trace_path.exists():
        phase1 = check_structural(tool_trace_path)
        structural = phase1.to_dict()
    else:
        structural = {
            "passed": True,
            "violations": [],
            "stats": {},
        }

    # Phase 2: Anti-Slop (content)
    if transcript_path.exists():
        prose = extract_prose(transcript_path)
        phase2 = score_text(prose)
        antislop = phase2.to_dict()
    else:
        antislop = {
            "score": 50,
            "passed": True,
            "dimensions": {},
            "violations": [],
            "word_count": 0,
        }

    # Phase 3: Canvas (structured output)
    if transcript_path.exists():
        phase3 = validate_canvas(transcript_path)
        canvas = phase3.to_dict()
    else:
        canvas = {
            "passed": True,
            "canvas_found": False,
            "errors": [],
        }

    # Overall pass/fail
    all_passed = (
        structural.get("passed", True)
        and antislop.get("passed", True)
        and canvas.get("passed", True)
    )

    # Summary
    parts = []
    if not structural.get("passed"):
        fail_count = len([v for v in structural.get("violations", []) if v.get("severity") == "FAIL"])
        parts.append(f"Structural: {fail_count} FAIL violations")
    if not antislop.get("passed"):
        parts.append(f"Anti-slop: {antislop.get('score', 0)}/50 (min 35)")
    if not canvas.get("passed"):
        parts.append(f"Canvas: {len(canvas.get('errors', []))} errors")

    summary = "ALL PASS" if all_passed else "FAIL — " + "; ".join(parts)

    return PipelineResult(
        passed=all_passed,
        structural=structural,
        antislop=antislop,
        canvas=canvas,
        summary=summary,
    )


def main():
    parser = argparse.ArgumentParser(description="Run Exocórtex audit pipeline")
    parser.add_argument("--transcript", type=Path, required=True,
                        help="Path to transcript.jsonl")
    parser.add_argument("--trace", type=Path, required=True,
                        help="Path to tool_trace.jsonl")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    args = parser.parse_args()

    result = audit(args.transcript, args.trace)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        status = "✅ PASS" if result.passed else "❌ FAIL"
        print(f"Auditor Pipeline: {status}")
        print(f"  Summary: {result.summary}")
        print()

        # Phase 1
        s = result.structural
        print(f"  Phase 1 — Structural: {'PASS' if s.get('passed') else 'FAIL'}")
        stats = s.get("stats", {})
        print(f"    Entries: {stats.get('total_entries', 0)}, "
              f"Tool calls: {stats.get('tool_calls', 0)}, "
              f"External: {stats.get('external_actions', 0)}, "
              f"Drafts: {stats.get('drafts_found', 0)}")
        for v in s.get("violations", [])[:5]:
            print(f"    [{v['severity']}] {v['rule']}: {v['evidence']}")

        # Phase 2
        a = result.antislop
        print(f"  Phase 2 — Anti-Slop: {'PASS' if a.get('passed') else 'FAIL'} "
              f"({a.get('score', 0)}/50)")
        for dim, score in a.get("dimensions", {}).items():
            print(f"    {dim}: {score}/10")

        # Phase 3
        c = result.canvas
        print(f"  Phase 3 — Canvas: {'PASS' if c.get('passed') else 'FAIL'}")
        if c.get("canvas_found"):
            print(f"    Schema valid: {c.get('schema_valid')}")
            print(f"    Alignment valid: {c.get('alignment_valid')}")
        for err in c.get("errors", [])[:3]:
            print(f"    ⚠ {err}")

    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
