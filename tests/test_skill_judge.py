#!/usr/bin/env python3
"""Unit tests for the Exocortex Skill Judge (scripts/skill_judge.py)."""

import json
import tempfile
import textwrap
import unittest
from pathlib import Path

from scripts.skill_judge import (
    parse_skill,
    check_d1_structural,
    compute_overall_verdict,
    collect_priority_fixes,
    discover_skills,
    generate_report,
    build_judge_prompt,
    VERDICTS,
)


def _write_skill(tmpdir: Path, name: str, content: str) -> Path:
    """Helper: write a SKILL.md to a temporary skill directory."""
    skill_dir = tmpdir / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(textwrap.dedent(content), encoding="utf-8")
    return skill_md


COMPLIANT_SKILL = """\
---
name: excrtx-test-compliant
description: A compliant test skill for unit testing
version: 1.0.0
category: excrtx
platforms:
  - linux
metadata:
  hermes:
    tags:
      - testing
      - quality
    related_skills:
      - excrtx-quality-gate
---

# Test Compliant Skill

## When to Use

Use this skill when testing the judge.

**Don't use for:** Production evaluation.

## Procedure

1. Parse the SKILL.md
2. Run D1 checks
3. Verify output

## Pitfalls

- Don't skip frontmatter fields
- Don't use line-numbered content

## Verification Checklist

- [ ] All frontmatter fields present
- [ ] All required sections present
"""

PARTIAL_SKILL = """\
---
name: excrtx-test-partial
description: A partial test skill missing pitfalls section
version: 1.0.0
category: excrtx
metadata:
  hermes:
    tags:
      - testing
---

# Test Partial Skill

## When to Use

Use this skill when testing partial compliance.

## Procedure

1. Do something

## Verification Checklist

- [ ] Check something
"""

NON_COMPLIANT_SKILL = """\
---
name: excrtx-test-noncompliant
version: 0.1.0
---

# Broken Skill

Some content without proper sections.
"""

SKILL_WITH_LINE_NUMBERS = """\
---
name: excrtx-test-linenums
description: A skill with line-numbering artifacts
version: 1.0.0
category: excrtx
metadata:
  hermes:
    tags:
      - testing
---

1|# Test Line Numbers
2|
3|## When to Use
4|
5|Use when testing line number detection.
6|
7|## Procedure
8|
9|1. Step one
10|
11|## Pitfalls
12|
13|- Pitfall one
14|
15|## Verification Checklist
16|
17|- [ ] Check
"""

SKILL_PT_BR_DESC = """\
---
name: excrtx-test-ptbr
description: Quando o executivo precisa criar e gerenciar configurações do sistema para ação
version: 1.0.0
category: excrtx
metadata:
  hermes:
    tags:
      - testing
---

# Test PT-BR

## When to Use

Use when testing.

## Procedure

1. Step one

## Pitfalls

- Issue one

## Verification Checklist

- [ ] Check
"""


class TestParseSkill(unittest.TestCase):
    """Tests for SKILL.md frontmatter and body parsing."""

    def test_parse_compliant_skill(self):
        with tempfile.TemporaryDirectory() as td:
            path = _write_skill(Path(td), "excrtx-test", COMPLIANT_SKILL)
            parsed = parse_skill(path)
            self.assertEqual(parsed["frontmatter"]["name"], "excrtx-test-compliant")
            self.assertEqual(parsed["frontmatter"]["version"], "1.0.0")
            self.assertFalse(parsed["has_line_numbers"])
            self.assertIn("Test Compliant Skill", parsed["body"])

    def test_parse_no_frontmatter(self):
        with tempfile.TemporaryDirectory() as td:
            path = _write_skill(Path(td), "excrtx-empty", "# No frontmatter\nJust body.")
            parsed = parse_skill(path)
            self.assertEqual(parsed["frontmatter"], {})
            self.assertIn("No frontmatter", parsed["body"])

    def test_parse_line_numbered_skill(self):
        with tempfile.TemporaryDirectory() as td:
            path = _write_skill(Path(td), "excrtx-lined", SKILL_WITH_LINE_NUMBERS)
            parsed = parse_skill(path)
            self.assertTrue(parsed["has_line_numbers"])
            # Should still parse the name despite line numbers in some content
            self.assertEqual(parsed["frontmatter"]["name"], "excrtx-test-linenums")

    def test_parse_size_tracking(self):
        with tempfile.TemporaryDirectory() as td:
            path = _write_skill(Path(td), "excrtx-size", COMPLIANT_SKILL)
            parsed = parse_skill(path)
            self.assertGreater(parsed["size_bytes"], 0)
            self.assertGreater(parsed["body_size_bytes"], 0)
            self.assertLess(parsed["body_size_bytes"], parsed["size_bytes"])


class TestD1Structural(unittest.TestCase):
    """Tests for deterministic D1 structural compliance checks."""

    def test_compliant_passes(self):
        with tempfile.TemporaryDirectory() as td:
            path = _write_skill(Path(td), "excrtx-ok", COMPLIANT_SKILL)
            parsed = parse_skill(path)
            d1 = check_d1_structural(parsed)
            self.assertEqual(d1["label"], "COMPLIANT")
            self.assertEqual(len(d1["issues"]), 0)

    def test_partial_detected(self):
        with tempfile.TemporaryDirectory() as td:
            path = _write_skill(Path(td), "excrtx-partial", PARTIAL_SKILL)
            parsed = parse_skill(path)
            d1 = check_d1_structural(parsed)
            self.assertEqual(d1["label"], "PARTIAL")
            # Missing pitfalls and verification sections
            section_issues = [i for i in d1["issues"] if "Missing section" in i]
            self.assertGreater(len(section_issues), 0)

    def test_non_compliant_detected(self):
        with tempfile.TemporaryDirectory() as td:
            path = _write_skill(Path(td), "excrtx-bad", NON_COMPLIANT_SKILL)
            parsed = parse_skill(path)
            d1 = check_d1_structural(parsed)
            self.assertEqual(d1["label"], "NON_COMPLIANT")
            # Should flag missing description, sections, etc.
            self.assertGreater(len(d1["issues"]), 2)

    def test_line_numbers_flagged(self):
        with tempfile.TemporaryDirectory() as td:
            path = _write_skill(Path(td), "excrtx-lines", SKILL_WITH_LINE_NUMBERS)
            parsed = parse_skill(path)
            d1 = check_d1_structural(parsed)
            line_issues = [i for i in d1["issues"] if "Line-numbering" in i]
            self.assertEqual(len(line_issues), 1)

    def test_ptbr_description_flagged(self):
        with tempfile.TemporaryDirectory() as td:
            path = _write_skill(Path(td), "excrtx-ptbr", SKILL_PT_BR_DESC)
            parsed = parse_skill(path)
            d1 = check_d1_structural(parsed)
            ptbr_issues = [i for i in d1["issues"] if "PT-BR" in i]
            self.assertEqual(len(ptbr_issues), 1)

    def test_missing_name_detected(self):
        skill = """\
        ---
        description: Valid description
        version: 1.0.0
        category: excrtx
        metadata:
          hermes:
            tags:
              - test
        ---

        # Title

        ## When to Use
        Use.

        ## Procedure
        1. Step.

        ## Pitfalls
        - Issue.

        ## Verification Checklist
        - [ ] Check.
        """
        with tempfile.TemporaryDirectory() as td:
            path = _write_skill(Path(td), "excrtx-noname", skill)
            parsed = parse_skill(path)
            d1 = check_d1_structural(parsed)
            name_issues = [i for i in d1["issues"] if "name" in i.lower()]
            self.assertGreater(len(name_issues), 0)

    def test_missing_tags_flagged(self):
        skill = """\
        ---
        name: excrtx-test-notags
        description: Valid description
        version: 1.0.0
        category: excrtx
        ---

        # Title

        ## When to Use
        Use.

        ## Procedure
        1. Step.

        ## Pitfalls
        - Issue.

        ## Verification Checklist
        - [ ] Check.
        """
        with tempfile.TemporaryDirectory() as td:
            path = _write_skill(Path(td), "excrtx-notags", skill)
            parsed = parse_skill(path)
            d1 = check_d1_structural(parsed)
            tags_issues = [i for i in d1["issues"] if "tags" in i.lower()]
            self.assertEqual(len(tags_issues), 1)

    def test_section_detection_case_insensitive(self):
        """Sections should be detected regardless of case."""
        skill = """\
        ---
        name: excrtx-test-case
        description: Case test
        version: 1.0.0
        category: excrtx
        metadata:
          hermes:
            tags:
              - test
        ---

        # Title

        ## WHEN TO USE
        Use.

        ## PROCEDURE
        1. Step.

        ## PITFALLS
        - Issue.

        ## VERIFICATION CHECKLIST
        - [ ] Check.
        """
        with tempfile.TemporaryDirectory() as td:
            path = _write_skill(Path(td), "excrtx-case", skill)
            parsed = parse_skill(path)
            d1 = check_d1_structural(parsed)
            self.assertEqual(d1["label"], "COMPLIANT")


class TestOverallVerdict(unittest.TestCase):
    """Tests for the overall verdict computation."""

    def test_all_best_is_pass(self):
        d1 = {"label": "COMPLIANT"}
        llm = {
            "D2_clarity": {"label": "CLEAR"},
            "D3_alignment": {"label": "ALIGNED"},
            "D4_fitness": {"label": "PRODUCTION_READY"},
            "D5_economy": {"label": "EFFICIENT"},
        }
        self.assertEqual(compute_overall_verdict(d1, llm), "PASS")

    def test_one_middle_is_improve(self):
        d1 = {"label": "COMPLIANT"}
        llm = {
            "D2_clarity": {"label": "AMBIGUOUS"},
            "D3_alignment": {"label": "ALIGNED"},
            "D4_fitness": {"label": "PRODUCTION_READY"},
            "D5_economy": {"label": "EFFICIENT"},
        }
        self.assertEqual(compute_overall_verdict(d1, llm), "IMPROVE")

    def test_two_middle_is_improve(self):
        d1 = {"label": "PARTIAL"}
        llm = {
            "D2_clarity": {"label": "AMBIGUOUS"},
            "D3_alignment": {"label": "ALIGNED"},
            "D4_fitness": {"label": "PRODUCTION_READY"},
            "D5_economy": {"label": "EFFICIENT"},
        }
        self.assertEqual(compute_overall_verdict(d1, llm), "IMPROVE")

    def test_three_middle_is_rewrite(self):
        d1 = {"label": "PARTIAL"}
        llm = {
            "D2_clarity": {"label": "AMBIGUOUS"},
            "D3_alignment": {"label": "PARTIAL"},
            "D4_fitness": {"label": "PRODUCTION_READY"},
            "D5_economy": {"label": "EFFICIENT"},
        }
        self.assertEqual(compute_overall_verdict(d1, llm), "REWRITE")

    def test_any_worst_is_rewrite(self):
        d1 = {"label": "COMPLIANT"}
        llm = {
            "D2_clarity": {"label": "VAGUE"},
            "D3_alignment": {"label": "ALIGNED"},
            "D4_fitness": {"label": "PRODUCTION_READY"},
            "D5_economy": {"label": "EFFICIENT"},
        }
        self.assertEqual(compute_overall_verdict(d1, llm), "REWRITE")

    def test_missing_llm_dims_defaults_worst(self):
        """When LLM dims are empty (D1-only mode), defaults should trigger REWRITE."""
        d1 = {"label": "COMPLIANT"}
        llm = {}
        self.assertEqual(compute_overall_verdict(d1, llm), "REWRITE")

    def test_d1_only_verdict_pass(self):
        """In D1-only mode, the CLI uses direct mapping not compute_overall_verdict."""
        d1 = {"label": "COMPLIANT"}
        verdict = "PASS" if d1["label"] == "COMPLIANT" else ("IMPROVE" if d1["label"] == "PARTIAL" else "REWRITE")
        self.assertEqual(verdict, "PASS")

    def test_d1_only_verdict_improve(self):
        d1 = {"label": "PARTIAL"}
        verdict = "PASS" if d1["label"] == "COMPLIANT" else ("IMPROVE" if d1["label"] == "PARTIAL" else "REWRITE")
        self.assertEqual(verdict, "IMPROVE")


class TestPriorityFixes(unittest.TestCase):
    """Tests for priority fix collection."""

    def test_mechanical_fixes_tagged(self):
        d1 = {"issues": ["Line-numbering artifacts detected (^\\d+|)"], "recommendations": []}
        fixes = collect_priority_fixes(d1, {})
        self.assertTrue(any("[D1-MECHANICAL]" in f for f in fixes))

    def test_section_fixes_tagged(self):
        d1 = {"issues": ["Missing section: pitfalls"], "recommendations": []}
        fixes = collect_priority_fixes(d1, {})
        self.assertTrue(any("[D1-SECTION]" in f for f in fixes))

    def test_translate_fixes_tagged(self):
        d1 = {"issues": ["Description appears to be in PT-BR (should be English for Hermes search)"], "recommendations": []}
        fixes = collect_priority_fixes(d1, {})
        self.assertTrue(any("[D1-TRANSLATE]" in f for f in fixes))

    def test_llm_recommendations_collected(self):
        d1 = {"issues": [], "recommendations": []}
        llm = {
            "D2_clarity": {"label": "AMBIGUOUS", "recommendations": ["Add counter-triggers"]},
            "D3_alignment": {"label": "ALIGNED", "recommendations": []},
        }
        fixes = collect_priority_fixes(d1, llm)
        self.assertTrue(any("counter-triggers" in f for f in fixes))


class TestDiscoverSkills(unittest.TestCase):
    """Tests for skill directory discovery."""

    def test_discovers_excrtx_skills(self):
        with tempfile.TemporaryDirectory() as td:
            tmpdir = Path(td)
            _write_skill(tmpdir, "excrtx-test-a", COMPLIANT_SKILL)
            _write_skill(tmpdir, "excrtx-test-b", COMPLIANT_SKILL)
            _write_skill(tmpdir, "non-excrtx-skill", COMPLIANT_SKILL)

            skills = discover_skills(tmpdir)
            names = [s.parent.name for s in skills]
            self.assertIn("excrtx-test-a", names)
            self.assertIn("excrtx-test-b", names)
            self.assertNotIn("non-excrtx-skill", names)

    def test_filter_by_name(self):
        with tempfile.TemporaryDirectory() as td:
            tmpdir = Path(td)
            _write_skill(tmpdir, "excrtx-test-a", COMPLIANT_SKILL)
            _write_skill(tmpdir, "excrtx-test-b", COMPLIANT_SKILL)

            skills = discover_skills(tmpdir, ["excrtx-test-a"])
            self.assertEqual(len(skills), 1)
            self.assertEqual(skills[0].parent.name, "excrtx-test-a")


class TestGenerateReport(unittest.TestCase):
    """Tests for report generation."""

    def test_report_contains_summary_table(self):
        results = [
            {
                "skill_name": "excrtx-test",
                "dimensions": {
                    "D1_structural": {"label": "COMPLIANT", "issues": []},
                },
                "overall_verdict": "PASS",
                "priority_fixes": [],
            }
        ]
        report = generate_report(results)
        self.assertIn("| Skill |", report)
        self.assertIn("excrtx-test", report)
        self.assertIn("PASS", report)

    def test_report_counts_verdicts(self):
        results = [
            {
                "skill_name": f"excrtx-test-{i}",
                "dimensions": {"D1_structural": {"label": "COMPLIANT", "issues": []}},
                "overall_verdict": v,
                "priority_fixes": [],
            }
            for i, v in enumerate(["PASS", "PASS", "IMPROVE"])
        ]
        report = generate_report(results)
        self.assertIn("PASS=2", report)
        self.assertIn("IMPROVE=1", report)


class TestBuildJudgePrompt(unittest.TestCase):
    """Tests for LLM judge prompt construction."""

    def test_prompt_includes_skill_name(self):
        with tempfile.TemporaryDirectory() as td:
            path = _write_skill(Path(td), "excrtx-test", COMPLIANT_SKILL)
            parsed = parse_skill(path)
            prompt = build_judge_prompt(parsed, "rubric text", "soul context")
            self.assertIn("excrtx-test-compliant", prompt)

    def test_prompt_includes_rubric_and_soul(self):
        with tempfile.TemporaryDirectory() as td:
            path = _write_skill(Path(td), "excrtx-test", COMPLIANT_SKILL)
            parsed = parse_skill(path)
            prompt = build_judge_prompt(parsed, "MY_RUBRIC_CONTENT", "MY_SOUL_CONTEXT")
            self.assertIn("MY_RUBRIC_CONTENT", prompt)
            self.assertIn("MY_SOUL_CONTEXT", prompt)

    def test_prompt_includes_output_format(self):
        with tempfile.TemporaryDirectory() as td:
            path = _write_skill(Path(td), "excrtx-test", COMPLIANT_SKILL)
            parsed = parse_skill(path)
            prompt = build_judge_prompt(parsed, "", "")
            self.assertIn("D2_clarity", prompt)
            self.assertIn("D3_alignment", prompt)
            self.assertIn("D4_fitness", prompt)
            self.assertIn("D5_economy", prompt)

    def test_prompt_includes_related_skills(self):
        with tempfile.TemporaryDirectory() as td:
            path = _write_skill(Path(td), "excrtx-test", COMPLIANT_SKILL)
            parsed = parse_skill(path)
            prompt = build_judge_prompt(parsed, "", "", related_skills=["skill-a", "skill-b"])
            self.assertIn("skill-a", prompt)
            self.assertIn("skill-b", prompt)


class TestBaselineComparison(unittest.TestCase):
    """Tests for baseline comparison logic."""

    def test_verdict_ordering(self):
        self.assertEqual(VERDICTS.index("PASS"), 0)
        self.assertEqual(VERDICTS.index("IMPROVE"), 1)
        self.assertEqual(VERDICTS.index("REWRITE"), 2)

    def test_regression_detection(self):
        """Simulate the regression detection logic from main()."""
        baseline = [
            {"skill_name": "excrtx-a", "overall_verdict": "PASS"},
            {"skill_name": "excrtx-b", "overall_verdict": "IMPROVE"},
        ]
        current = [
            {"skill_name": "excrtx-a", "overall_verdict": "IMPROVE"},  # regression
            {"skill_name": "excrtx-b", "overall_verdict": "PASS"},  # improvement
        ]
        baseline_map = {r["skill_name"]: r for r in baseline}
        regressions = []
        improvements = []
        for r in current:
            b = baseline_map.get(r["skill_name"])
            if not b:
                continue
            b_idx = VERDICTS.index(b["overall_verdict"])
            r_idx = VERDICTS.index(r["overall_verdict"])
            if r_idx > b_idx:
                regressions.append(r["skill_name"])
            elif r_idx < b_idx:
                improvements.append(r["skill_name"])

        self.assertEqual(regressions, ["excrtx-a"])
        self.assertEqual(improvements, ["excrtx-b"])


class TestCompileSoulValidation(unittest.TestCase):
    """Tests for compile_soul.py --validate-compiled-rules."""

    def test_import_validate_function(self):
        from scripts.compile_soul import validate_compiled_rules
        self.assertTrue(callable(validate_compiled_rules))

    def test_synced_rules_pass(self):
        from scripts.compile_soul import validate_compiled_rules
        skill = """\
---
name: excrtx-test-synced
description: Test synced rules
version: 1.0.0
compiled_rules: |
  Use the vetor classification table.
  Apply draft-first protocol for external actions.
---

# Test Synced

## When to Use
Use for testing vetor classification.

## Procedure
1. Check the vetor classification table
2. Apply draft-first protocol for external actions
"""
        with tempfile.TemporaryDirectory() as td:
            _write_skill(Path(td), "excrtx-test", skill)
            desyncs = validate_compiled_rules(Path(td))
            self.assertEqual(len(desyncs), 0)


if __name__ == "__main__":
    unittest.main()
