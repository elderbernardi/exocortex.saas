#!/usr/bin/env python3
"""
Tests for scripts/validate_frontmatter.py.

Exercises the 7 frontmatter fixtures in tests/fixtures/frontmatter/ via
subprocess so the validator is tested as-invoked (not as an imported module).
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = REPO_ROOT / "scripts" / "validate_frontmatter.py"
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures" / "frontmatter"


def _run(fixture_name: str) -> subprocess.CompletedProcess:
    path = FIXTURES_DIR / fixture_name
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--file", str(path)],
        capture_output=True,
        text=True,
    )


# ─── Valid fixtures — must exit 0 ───────────────────────────────────────────

class TestValidFixtures:
    def test_valid_volatile(self):
        result = _run("valid-volatile.md")
        assert result.returncode == 0, result.stdout + result.stderr

    def test_valid_perene(self):
        result = _run("valid-perene.md")
        assert result.returncode == 0, result.stdout + result.stderr

    def test_valid_deprecated(self):
        result = _run("valid-deprecated.md")
        assert result.returncode == 0, result.stdout + result.stderr

    def test_valid_promoted(self):
        result = _run("valid-promoted.md")
        assert result.returncode == 0, result.stdout + result.stderr

    def test_valid_with_utf8_bom(self):
        # A leading UTF-8 BOM must not trip V-001 (regression: BOM stripping).
        result = _run("valid-bom.md")
        assert result.returncode == 0, result.stdout + result.stderr
        assert "V-001" not in (result.stdout + result.stderr)


# ─── Invalid fixtures — must exit 1 and name a rule ID ──────────────────────

class TestInvalidFixtures:
    def test_missing_type_exits_1(self):
        result = _run("invalid-missing-type.md")
        assert result.returncode == 1, result.stdout + result.stderr

    def test_missing_type_reports_rule_id(self):
        result = _run("invalid-missing-type.md")
        output = result.stdout + result.stderr
        # V-010 is the mandatory `type` field rule
        assert "V-010" in output or "type" in output.lower(), (
            f"Expected rule ID in output, got: {output}"
        )

    def test_bad_class_exits_1(self):
        result = _run("invalid-bad-class.md")
        assert result.returncode == 1, result.stdout + result.stderr

    def test_bad_class_reports_rule_id(self):
        result = _run("invalid-bad-class.md")
        output = result.stdout + result.stderr
        # V-041 is the class vocabulary rule
        assert "V-041" in output or "class" in output.lower(), (
            f"Expected rule ID in output, got: {output}"
        )

    def test_deprecated_no_reason_exits_1(self):
        result = _run("invalid-deprecated-no-reason.md")
        assert result.returncode == 1, result.stdout + result.stderr

    def test_deprecated_no_reason_reports_rule_id(self):
        result = _run("invalid-deprecated-no-reason.md")
        output = result.stdout + result.stderr
        # V-060 range covers deprecated field rules
        assert any(f"V-06{d}" in output for d in range(10)) or "deprecated_reason" in output, (
            f"Expected deprecation rule ID in output, got: {output}"
        )


# ─── Edge cases ─────────────────────────────────────────────────────────────

class TestEdgeCases:
    def test_nonexistent_file_exits_2(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "--file", str(FIXTURES_DIR / "nonexistent.md")],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 2, result.stdout + result.stderr

    def test_dir_mode_on_fixtures_dir(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "--dir", str(FIXTURES_DIR)],
            capture_output=True,
            text=True,
        )
        # Fixtures dir has both valid and invalid files — should exit 1
        assert result.returncode == 1, (
            "Expected exit 1 (mixed valid/invalid fixtures), got: "
            + result.stdout + result.stderr
        )


class TestScopeExcludes:
    """--dir skips non-semantic areas (_artifacts/, raw/, README, ...) by default."""

    def _build_tree(self, tmp_path):
        # one valid semantic page
        (tmp_path / "micro" / "x" / "knowledge").mkdir(parents=True)
        (tmp_path / "micro" / "x" / "knowledge" / "ok.md").write_text(
            (FIXTURES_DIR / "valid-volatile.md").read_text()
        )
        # non-semantic files that lack frontmatter (would fail V-001 if validated)
        (tmp_path / "_artifacts" / "items" / "a").mkdir(parents=True)
        (tmp_path / "_artifacts" / "items" / "a" / "source.md").write_text("# no frontmatter\n")
        (tmp_path / "raw").mkdir()
        (tmp_path / "raw" / "dump.md").write_text("raw dump, no frontmatter\n")
        (tmp_path / "README.md").write_text("# Readme, no frontmatter\n")

    def test_excluded_by_default(self, tmp_path):
        self._build_tree(tmp_path)
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "--dir", str(tmp_path)],
            capture_output=True, text=True,
        )
        out = result.stdout + result.stderr
        assert result.returncode == 0, out          # only the valid page is checked
        # the excluded files are never validated (their paths don't appear as results)
        assert "source.md" not in out
        assert "dump.md" not in out
        assert "ok.md" in out                        # the semantic page was validated
        assert "Skipped" in out

    def test_no_exclude_validates_everything(self, tmp_path):
        self._build_tree(tmp_path)
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "--dir", str(tmp_path), "--no-exclude"],
            capture_output=True, text=True,
        )
        # the non-semantic files now fail V-001 → exit 1
        assert result.returncode == 1, result.stdout + result.stderr
