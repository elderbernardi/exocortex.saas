#!/usr/bin/env python3
"""Focused tests for issue #56 metadata and baseline workflows."""

import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from scripts.skill_judge import check_d1_structural, parse_skill

REPO_ROOT = Path(__file__).resolve().parents[1]


def _write_skill(tmpdir: Path, name: str, content: str) -> Path:
    skill_dir = tmpdir / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    path = skill_dir / "SKILL.md"
    path.write_text(textwrap.dedent(content), encoding="utf-8")
    return path


class SkillGateMetadataTest(unittest.TestCase):
    def test_production_skill_requires_gate_block(self):
        skill = """\
---
name: excrtx-produce-slides
description: Production skill without gate metadata
version: 1.0.0
category: excrtx
metadata:
  hermes:
    tags:
      - production
---

# Produce Slides

## When to Use
Use this skill for premium slide generation.

## Procedure
1. Build the artifact.

## Pitfalls
- Do not skip validation.

## Verification Checklist
- [ ] Output validated.
"""
        with tempfile.TemporaryDirectory() as td:
            parsed = parse_skill(_write_skill(Path(td), "excrtx-produce-slides", skill))
            d1 = check_d1_structural(parsed)
            self.assertIn("Missing 'gate' block for production skill", d1["issues"])

    def test_gate_max_context_tokens_must_be_positive_int(self):
        skill = """\
---
name: excrtx-produce-artifacts
description: Production skill with broken gate metadata
version: 1.0.0
category: excrtx
gate:
  require_quality_gate: true
  max_context_tokens: zero
metadata:
  hermes:
    tags:
      - production
---

# Produce Artifacts

## When to Use
Use this skill for exports.

## Procedure
1. Build the artifact.

## Pitfalls
- Do not skip validation.

## Verification Checklist
- [ ] Output validated.
"""
        with tempfile.TemporaryDirectory() as td:
            parsed = parse_skill(_write_skill(Path(td), "excrtx-produce-artifacts", skill))
            d1 = check_d1_structural(parsed)
            self.assertIn("gate.max_context_tokens must be a positive integer", d1["issues"])

    def test_gate_metadata_validates_when_present(self):
        skill = """\
---
name: excrtx-produce-oficios
description: Production skill with gate metadata
version: 1.0.0
category: excrtx
gate:
  require_quality_gate: true
  max_context_tokens: 2000
metadata:
  hermes:
    tags:
      - production
---

# Produce Ofícios

## When to Use
Use this skill for ofícios.

## Procedure
1. Build the artifact.

## Pitfalls
- Do not skip validation.

## Verification Checklist
- [ ] Output validated.
"""
        with tempfile.TemporaryDirectory() as td:
            parsed = parse_skill(_write_skill(Path(td), "excrtx-produce-oficios", skill))
            d1 = check_d1_structural(parsed)
            gate_issues = [issue for issue in d1["issues"] if issue.startswith("Missing gate") or issue.startswith("gate.")]
            self.assertEqual(gate_issues, [])


class SaveBaselineCliTest(unittest.TestCase):
    def test_save_baseline_writes_json_file(self):
        with tempfile.TemporaryDirectory() as td:
            baseline_path = Path(td) / "skill-judge-baseline.json"
            cmd = [
                sys.executable,
                "scripts/skill_judge.py",
                "--skill",
                "excrtx-behavior-vetor",
                "--d1-only",
                "--save-baseline",
                str(baseline_path),
            ]
            result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertTrue(baseline_path.exists())
            payload = json.loads(baseline_path.read_text(encoding="utf-8"))
            self.assertEqual(payload[0]["skill_name"], "excrtx-behavior-vetor")


if __name__ == "__main__":
    unittest.main()
