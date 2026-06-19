#!/usr/bin/env python3
"""
Tests for scripts/migrate_frontmatter.py.

Creates temporary directories with pre-migration content, runs the migrator,
and verifies field transformations and validator compliance.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MIGRATOR = REPO_ROOT / "scripts" / "migrate_frontmatter.py"
VALIDATOR = REPO_ROOT / "scripts" / "validate_frontmatter.py"

# Pre-migration content with old schema
_OLD_SCHEMA_CONTENT = """\
---
title: "Preço do Produto"
created: "2026-06-01"
updated: "2026-06-10"
nature: knowledge
type: fact
tags: [produto, preco]
confidence: medium
---

# Preço do Produto

Preço atual: R$ 150,00.
"""

# Content with no frontmatter at all (should be skipped without error)
_NO_FRONTMATTER_CONTENT = """\
# Arquivo sem frontmatter

Conteúdo sem cabeçalho YAML.
"""


def _make_acervo_file(base: Path, rel_path: str, content: str) -> Path:
    """Write content under base/micro/test-domain/<rel_path>."""
    target = base / "micro" / "test-domain" / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target


def _run_migrator(target_dir: Path, *extra_args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(MIGRATOR), "--dir", str(target_dir)] + list(extra_args),
        capture_output=True,
        text=True,
    )


def _run_validator(file_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--file", str(file_path)],
        capture_output=True,
        text=True,
    )


# ─── Core migration rules ────────────────────────────────────────────────────

class TestCoreMigrationRules:
    def test_exits_0_on_success(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            _make_acervo_file(base, "knowledge/preco.md", _OLD_SCHEMA_CONTENT)
            result = _run_migrator(base)
            assert result.returncode == 0, result.stdout + result.stderr

    def test_old_type_renamed_to_excrtx_type(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            target = _make_acervo_file(base, "knowledge/preco.md", _OLD_SCHEMA_CONTENT)
            _run_migrator(base)
            migrated = target.read_text(encoding="utf-8")
            assert "excrtx_type:" in migrated, (
                "Expected old 'type' to be renamed to 'excrtx_type'"
            )
            assert "excrtx_type: fact" in migrated

    def test_okf_type_field_added(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            target = _make_acervo_file(base, "knowledge/preco.md", _OLD_SCHEMA_CONTENT)
            _run_migrator(base)
            migrated = target.read_text(encoding="utf-8")
            # OKF 'type' must appear as a standalone field (not excrtx_type)
            import re
            assert re.search(r"^type:\s+\w+", migrated, re.MULTILINE), (
                "Expected OKF 'type' field in migrated frontmatter"
            )

    def test_class_field_added(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            target = _make_acervo_file(base, "knowledge/preco.md", _OLD_SCHEMA_CONTENT)
            _run_migrator(base)
            migrated = target.read_text(encoding="utf-8")
            assert "class:" in migrated, "Expected 'class' field in migrated frontmatter"

    def test_timestamp_field_added(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            target = _make_acervo_file(base, "knowledge/preco.md", _OLD_SCHEMA_CONTENT)
            _run_migrator(base)
            migrated = target.read_text(encoding="utf-8")
            assert "timestamp:" in migrated, "Expected 'timestamp' field in migrated frontmatter"

    def test_created_at_field_added(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            target = _make_acervo_file(base, "knowledge/preco.md", _OLD_SCHEMA_CONTENT)
            _run_migrator(base)
            migrated = target.read_text(encoding="utf-8")
            assert "created_at:" in migrated, "Expected 'created_at' field in migrated frontmatter"

    def test_description_field_added(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            target = _make_acervo_file(base, "knowledge/preco.md", _OLD_SCHEMA_CONTENT)
            _run_migrator(base)
            migrated = target.read_text(encoding="utf-8")
            assert "description:" in migrated, "Expected 'description' field in migrated frontmatter"


# ─── Validator compliance ────────────────────────────────────────────────────

class TestValidatorCompliance:
    def test_migrated_file_passes_validator(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            target = _make_acervo_file(base, "knowledge/preco.md", _OLD_SCHEMA_CONTENT)
            migrator_result = _run_migrator(base)
            assert migrator_result.returncode == 0, migrator_result.stdout + migrator_result.stderr
            validator_result = _run_validator(target)
            assert validator_result.returncode == 0, (
                f"Migrated file failed validation:\n{validator_result.stdout}{validator_result.stderr}"
            )

    def test_dry_run_does_not_modify_file(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            target = _make_acervo_file(base, "knowledge/preco.md", _OLD_SCHEMA_CONTENT)
            original = target.read_text(encoding="utf-8")
            _run_migrator(base, "--dry-run")
            after = target.read_text(encoding="utf-8")
            assert original == after, "Dry-run should not modify the file"


# ─── Edge cases ─────────────────────────────────────────────────────────────

class TestEdgeCases:
    def test_nonexistent_dir_exits_nonzero(self):
        result = subprocess.run(
            [sys.executable, str(MIGRATOR), "--dir", "/nonexistent/path/xyz"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0

    def test_already_migrated_file_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            target = _make_acervo_file(base, "knowledge/preco.md", _OLD_SCHEMA_CONTENT)
            _run_migrator(base)
            first_pass = target.read_text(encoding="utf-8")
            _run_migrator(base)
            second_pass = target.read_text(encoding="utf-8")
            # Running migrator twice should not double-add fields
            assert first_pass.count("excrtx_type:") == second_pass.count("excrtx_type:"), (
                "Migration is not idempotent: excrtx_type appears different number of times"
            )
