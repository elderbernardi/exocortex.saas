#!/usr/bin/env python3
"""
Tests for the WARN/ERROR severity tiers in scripts/validate_frontmatter.py.

schema-spec.md (Section: Validation Rules) defines six WARN-severity rules —
V-004, V-022, V-025, V-026, V-072, V-075. WARN violations must be reported
but exit 0; any ERROR violation must exit 1. Uses tmp_path-generated files
and invokes the validator via subprocess (as-invoked, not imported).
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = REPO_ROOT / "scripts" / "validate_frontmatter.py"

VALID_TEMPLATE = """\
---
type: knowledge
title: Severity tier test file
description: "{description}"
tags:
  - test
timestamp: 2026-07-03
class: perene
created_at: 2026-07-03T10:00:00Z
---

Non-empty body content.
"""


def _run(path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--file", str(path)],
        capture_output=True,
        text=True,
    )


# ─── WARN tier — reported, but exit 0 ───────────────────────────────────────

class TestWarnTier:
    def test_long_description_exits_0(self, tmp_path):
        # V-026: description > 120 chars is WARN, not ERROR
        md = tmp_path / "long-description.md"
        md.write_text(VALID_TEMPLATE.format(description="x" * 130), encoding="utf-8")
        result = _run(md)
        assert result.returncode == 0, result.stdout + result.stderr

    def test_long_description_reports_warn(self, tmp_path):
        md = tmp_path / "long-description.md"
        md.write_text(VALID_TEMPLATE.format(description="x" * 130), encoding="utf-8")
        result = _run(md)
        output = result.stdout + result.stderr
        assert "V-026" in output, f"Expected V-026 in output, got: {output}"
        assert "WARN" in output, f"Expected WARN severity in output, got: {output}"
        assert "ERROR" not in output, f"Expected no ERROR in output, got: {output}"


# ─── ERROR tier — exit 1 ────────────────────────────────────────────────────

class TestErrorTier:
    def test_missing_type_exits_1(self, tmp_path):
        # V-010: missing `type` is ERROR
        content = VALID_TEMPLATE.format(description="Short and valid description.")
        content = content.replace("type: knowledge\n", "")
        md = tmp_path / "missing-type.md"
        md.write_text(content, encoding="utf-8")
        result = _run(md)
        assert result.returncode == 1, result.stdout + result.stderr
        output = result.stdout + result.stderr
        assert "V-010" in output, f"Expected V-010 in output, got: {output}"
