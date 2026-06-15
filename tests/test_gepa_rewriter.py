#!/usr/bin/env python3
"""Unit tests for the GEPA system (gepa_rewriter.py and gepa_loop.py)."""

import json
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from scripts.gepa_rewriter import (
    validate_rewrite,
    build_rewrite_prompt,
    rewrite_skill,
    RewriteResult,
)
from scripts.gepa_loop import (
    process_skill,
    _save_audit_log,
)


MOCK_ORIGINAL_SKILL = """\
---
name: excrtx-test-skill
description: A mock skill for unit testing GEPA
version: 1.0.0
category: excrtx
compiled_rules: |
  Rule 1
  Rule 2
metadata:
  hermes:
    tags:
      - test
    calibration:
      - calibration_prompt: "prompt"
        test_prompt: "test"
        acceptance_criteria: "crit"
        remediation_tip: "tip"
---

# Mock Skill Title

## When to Use

Use this skill when testing GEPA functionality.

## Procedure

1. Parse the skill.
2. Run the tests.

## Pitfalls

- Don't skip these pitfalls.

## Verification Checklist

- [ ] Check one.
"""

MOCK_VALID_REWRITE = """\
---
name: excrtx-test-skill
description: A mock skill for unit testing GEPA - updated
version: 1.0.0
category: excrtx
compiled_rules: |
  Rule 1
  Rule 2
metadata:
  hermes:
    tags:
      - test
    calibration:
      - calibration_prompt: "prompt"
        test_prompt: "test"
        acceptance_criteria: "crit"
        remediation_tip: "tip"
---

# Mock Skill Title Updated

## When to Use

Use this skill when testing GEPA functionality.

## Procedure

1. Parse the skill.
2. Run the tests and review results.

## Pitfalls

- Don't skip these pitfalls.

## Verification Checklist

- [ ] Check one.
"""


class TestGepaRewriter(unittest.TestCase):
    """Tests for the rewriter validation and prompting rules."""

    def test_validate_rewrite_valid(self):
        errors = validate_rewrite(MOCK_ORIGINAL_SKILL, MOCK_VALID_REWRITE)
        self.assertEqual(len(errors), 0, f"Expected no errors, got: {errors}")

    def test_validate_rewrite_missing_section(self):
        # Remove Procedure section
        invalid_rewrite = MOCK_VALID_REWRITE.replace("## Procedure", "## RemovedSection")
        errors = validate_rewrite(MOCK_ORIGINAL_SKILL, invalid_rewrite)
        self.assertTrue(any("Missing required section: procedure" in e for e in errors))

    def test_validate_rewrite_modified_compiled_rules(self):
        # Modify compiled_rules
        invalid_rewrite = MOCK_VALID_REWRITE.replace("Rule 2", "Rule 2 Modified")
        errors = validate_rewrite(MOCK_ORIGINAL_SKILL, invalid_rewrite)
        self.assertTrue(any("compiled_rules was modified" in e for e in errors))

    def test_validate_rewrite_removed_compiled_rules(self):
        # Remove compiled_rules field
        invalid_rewrite = MOCK_VALID_REWRITE.replace("compiled_rules: |\n  Rule 1\n  Rule 2", "")
        errors = validate_rewrite(MOCK_ORIGINAL_SKILL, invalid_rewrite)
        self.assertTrue(any("compiled_rules was removed" in e for e in errors))

    def test_validate_rewrite_modified_calibration(self):
        # Modify test_prompt calibration field
        invalid_rewrite = MOCK_VALID_REWRITE.replace('"test"', '"test_modified"')
        errors = validate_rewrite(MOCK_ORIGINAL_SKILL, invalid_rewrite)
        self.assertTrue(any("calibration.test_prompt was modified" in e for e in errors))

    def test_validate_rewrite_changed_version_or_name(self):
        # Change version
        invalid_rewrite = MOCK_VALID_REWRITE.replace("version: 1.0.0", "version: 1.0.1")
        errors = validate_rewrite(MOCK_ORIGINAL_SKILL, invalid_rewrite)
        self.assertTrue(any("Version changed" in e for e in errors))

        # Change name
        invalid_rewrite = MOCK_VALID_REWRITE.replace("name: excrtx-test-skill", "name: excrtx-new-name")
        errors = validate_rewrite(MOCK_ORIGINAL_SKILL, invalid_rewrite)
        self.assertTrue(any("Name changed" in e for e in errors))

    def test_build_rewrite_prompt(self):
        judge_result = {
            "priority_fixes": ["Fix pitfall formatting", "Add missing trigger"],
            "dimensions": {"D2_clarity": {"label": "AMBIGUOUS", "reasoning": "Reasoning info"}}
        }
        for strategy in ["targeted", "comprehensive", "minimal"]:
            prompt = build_rewrite_prompt(
                "excrtx-test-skill",
                MOCK_ORIGINAL_SKILL,
                judge_result,
                "rubric text excerpt",
                "soul context",
                strategy
            )
            self.assertIn("excrtx-test-skill", prompt)
            if strategy in ("targeted", "comprehensive"):
                self.assertIn("Fix pitfall formatting", prompt)
                self.assertIn("soul context", prompt)
            elif strategy == "minimal":
                self.assertIn("Add missing trigger", prompt)

    @patch("scripts.gepa_rewriter._call_rewrite_llm")
    def test_rewrite_skill_success(self, mock_llm):
        mock_llm.return_value = (MOCK_VALID_REWRITE, "deepseek-v4-pro")
        
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "SKILL.md"
            path.write_text(MOCK_ORIGINAL_SKILL, encoding="utf-8")
            
            judge_result = {"priority_fixes": ["Improve details"]}
            result = rewrite_skill(
                "excrtx-test-skill",
                path,
                judge_result,
                "rubric text",
                "soul context",
                "targeted"
            )
            self.assertTrue(result.success)
            self.assertEqual(result.new_content, MOCK_VALID_REWRITE.strip())
            self.assertEqual(result.llm_model, "deepseek-v4-pro")

    @patch("scripts.gepa_rewriter._call_rewrite_llm")
    def test_rewrite_skill_validation_failure(self, mock_llm):
        # Return invalid rewrite (missing procedure)
        invalid_rewrite = MOCK_VALID_REWRITE.replace("## Procedure", "## Removed")
        mock_llm.return_value = (invalid_rewrite, "deepseek-v4-pro")
        
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "SKILL.md"
            path.write_text(MOCK_ORIGINAL_SKILL, encoding="utf-8")
            
            judge_result = {"priority_fixes": ["Improve details"]}
            result = rewrite_skill(
                "excrtx-test-skill",
                path,
                judge_result,
                "rubric text",
                "soul context",
                "targeted"
            )
            self.assertFalse(result.success)
            self.assertGreater(len(result.validation_errors), 0)


class TestGepaLoop(unittest.TestCase):
    """Tests for the loop orchestrator and safety gates."""

    @patch("scripts.gepa_loop._judge_skill_full")
    @patch("scripts.gepa_loop.rewrite_skill")
    @patch("scripts.gepa_loop._git_commit_skill")
    def test_accept_gate_improves_verdict(self, mock_commit, mock_rewrite, mock_judge):
        # Mocking: rewrite succeeds, and re-judge improves verdict from IMPROVE to PASS
        mock_rewrite.return_value = RewriteResult(
            success=True,
            new_content=MOCK_VALID_REWRITE,
            changes_summary="Improved description",
            llm_model="deepseek-v4-pro"
        )
        mock_judge.return_value = {
            "overall_verdict": "PASS",
            "priority_fixes": [],
            "dimensions": {"D1_structural": {"label": "COMPLIANT"}}
        }

        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "SKILL.md"
            path.write_text(MOCK_ORIGINAL_SKILL, encoding="utf-8")

            judge_result = {"overall_verdict": "IMPROVE"}
            entry = process_skill(
                "excrtx-test-skill",
                path,
                judge_result,
                "rubric_text",
                "soul_context",
                max_attempts=1,
                dry_run=False,
                auto_commit=True
            )

            self.assertEqual(entry["before_verdict"], "IMPROVE")
            self.assertEqual(entry["after_verdict"], "PASS")
            self.assertEqual(entry["attempts"], 1)
            mock_commit.assert_called_once()
            # Verify file was modified
            self.assertEqual(path.read_text(encoding="utf-8"), MOCK_VALID_REWRITE)

    @patch("scripts.gepa_loop._judge_skill_full")
    @patch("scripts.gepa_loop.rewrite_skill")
    @patch("scripts.gepa_loop._git_commit_skill")
    def test_reject_gate_no_improvement(self, mock_commit, mock_rewrite, mock_judge):
        # Mocking: rewrite succeeds, but re-judge doesn't improve verdict (stays IMPROVE)
        mock_rewrite.return_value = RewriteResult(
            success=True,
            new_content=MOCK_VALID_REWRITE,
            changes_summary="Improved description",
            llm_model="deepseek-v4-pro"
        )
        mock_judge.return_value = {
            "overall_verdict": "IMPROVE",
            "priority_fixes": ["Keep improving"],
            "dimensions": {"D1_structural": {"label": "COMPLIANT"}}
        }

        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "SKILL.md"
            path.write_text(MOCK_ORIGINAL_SKILL, encoding="utf-8")

            judge_result = {"overall_verdict": "IMPROVE"}
            entry = process_skill(
                "excrtx-test-skill",
                path,
                judge_result,
                "rubric_text",
                "soul_context",
                max_attempts=1,
                dry_run=False,
                auto_commit=True
            )

            self.assertEqual(entry["before_verdict"], "IMPROVE")
            self.assertEqual(entry["after_verdict"], "IMPROVE")
            self.assertEqual(entry["attempts"], 1)
            mock_commit.assert_not_called()
            # File should be rolled back to original content
            self.assertEqual(path.read_text(encoding="utf-8"), MOCK_ORIGINAL_SKILL)

    @patch("scripts.gepa_loop._judge_skill_full")
    @patch("scripts.gepa_loop.rewrite_skill")
    def test_d1_hard_reject_on_regression(self, mock_rewrite, mock_judge):
        # Mocking: rewrite succeeds, but introduces D1 regression (missing procedure)
        regressed_content = MOCK_VALID_REWRITE.replace("## Procedure", "## Removed")
        mock_rewrite.return_value = RewriteResult(
            success=True,
            new_content=regressed_content,
            changes_summary="Removed procedure",
            llm_model="deepseek-v4-pro"
        )

        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "SKILL.md"
            path.write_text(MOCK_ORIGINAL_SKILL, encoding="utf-8")

            judge_result = {"overall_verdict": "IMPROVE"}
            entry = process_skill(
                "excrtx-test-skill",
                path,
                judge_result,
                "rubric_text",
                "soul_context",
                max_attempts=1,
                dry_run=False,
                auto_commit=True
            )

            self.assertTrue(entry["d1_regression"])
            self.assertIn("D1 regressed", entry["error"])
            # File should be rolled back to original content
            self.assertEqual(path.read_text(encoding="utf-8"), MOCK_ORIGINAL_SKILL)
            mock_judge.assert_not_called()

    @patch("scripts.gepa_loop.rewrite_skill")
    def test_dry_run_no_writes(self, mock_rewrite):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "SKILL.md"
            path.write_text(MOCK_ORIGINAL_SKILL, encoding="utf-8")

            judge_result = {"overall_verdict": "IMPROVE"}
            entry = process_skill(
                "excrtx-test-skill",
                path,
                judge_result,
                "rubric_text",
                "soul_context",
                max_attempts=1,
                dry_run=True,
                auto_commit=True
            )

            mock_rewrite.assert_not_called()
            self.assertEqual(path.read_text(encoding="utf-8"), MOCK_ORIGINAL_SKILL)
            self.assertEqual(entry["changes_summary"], "dry-run: no changes")

    @patch("scripts.gepa_loop.RUNS_DIR")
    def test_audit_log_created(self, mock_runs_dir):
        with tempfile.TemporaryDirectory() as td:
            mock_runs_dir_path = Path(td)
            # Patch the module-level RUNS_DIR using target mapping
            with patch("scripts.gepa_loop.RUNS_DIR", mock_runs_dir_path):
                entries = [{
                    "skill": "excrtx-test-skill",
                    "before_verdict": "IMPROVE",
                    "after_verdict": "PASS",
                    "attempts": 1,
                    "strategy_used": "targeted",
                    "llm_model": "deepseek-v4-pro",
                    "changes_summary": "Improved description",
                    "d1_regression": False,
                    "error": None,
                }]
                _save_audit_log(entries, "gepa-test-run")

                expected_file = mock_runs_dir_path / "gepa-test-run.json"
                self.assertTrue(expected_file.exists())
                log_data = json.loads(expected_file.read_text(encoding="utf-8"))
                self.assertEqual(log_data["run_id"], "gepa-test-run")
                self.assertEqual(log_data["skills_promoted"], 1)


if __name__ == "__main__":
    unittest.main()
