#!/usr/bin/env python3
"""Generate local draft issues for non-PASS dogfood results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from scripts.dogfood_features import render_issue_draft, validate_result_payload
    from scripts.dogfood_validate_catalog import parse_simple_yaml
except ModuleNotFoundError:
    from dogfood_features import render_issue_draft, validate_result_payload
    from dogfood_validate_catalog import parse_simple_yaml


def generate_issue_drafts(run_dir: Path) -> list[Path]:
    written: list[Path] = []
    for result_path in sorted(run_dir.glob("EX-*/result.json")):
        feature_dir = result_path.parent
        result = json.loads(result_path.read_text(encoding="utf-8"))
        validate_result_payload(result)
        if result["status"] == "PASS":
            continue
        scenario_path = feature_dir / "scenario.yaml"
        scenario = parse_simple_yaml(scenario_path.read_text(encoding="utf-8"))
        draft_path = feature_dir / "draft-issue.md"
        draft_path.write_text(render_issue_draft(scenario, result, feature_dir), encoding="utf-8")
        written.append(draft_path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir")
    args = parser.parse_args()
    written = generate_issue_drafts(Path(args.run_dir))
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
