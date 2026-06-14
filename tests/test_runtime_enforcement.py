#!/usr/bin/env python3
"""Tests for runtime enforcement helpers introduced by issue #56."""

import tempfile
import unittest
from pathlib import Path

from scripts.exocortex_runtime_guard import (
    enforce_skill_gate,
    guard_write_path,
    resolve_active_microverso,
)


class RuntimeSkillGateTest(unittest.TestCase):
    def test_production_skill_without_quality_gate_is_rejected(self):
        result = enforce_skill_gate(
            "excrtx-produce-slides",
            loaded_skills=["excrtx-produce-artifacts"],
            estimated_context_tokens=1200,
        )
        self.assertFalse(result["allowed"])
        self.assertEqual(result["reason"], "quality_gate_required")

    def test_production_skill_with_quality_gate_is_allowed(self):
        result = enforce_skill_gate(
            "excrtx-produce-slides",
            loaded_skills=["excrtx-produce-artifacts", "excrtx-quality-gate"],
            estimated_context_tokens=1200,
        )
        self.assertTrue(result["allowed"])
        self.assertEqual(result["reason"], "passed")

    def test_context_budget_exceeded_is_rejected(self):
        result = enforce_skill_gate(
            "excrtx-produce-artifacts",
            loaded_skills=["excrtx-quality-gate"],
            estimated_context_tokens=2501,
        )
        self.assertFalse(result["allowed"])
        self.assertEqual(result["reason"], "context_budget_exceeded")


class RuntimeWriteScopeTest(unittest.TestCase):
    def test_guard_write_allows_within_active_microverso(self):
        with tempfile.TemporaryDirectory() as td:
            acervo_root = Path(td) / "acervo"
            allowed = acervo_root / "micro" / "gabinete" / "knowledge"
            allowed.mkdir(parents=True, exist_ok=True)
            target = allowed / "nota.md"
            result = guard_write_path(target, active_microverso="gabinete", acervo_root=acervo_root)
            self.assertTrue(result["allowed"])
            self.assertEqual(result["reason"], "within_active_microverso")

    def test_guard_write_blocks_cross_microverso_path(self):
        with tempfile.TemporaryDirectory() as td:
            acervo_root = Path(td) / "acervo"
            target = acervo_root / "micro" / "ensino" / "knowledge" / "nota.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            result = guard_write_path(target, active_microverso="gabinete", acervo_root=acervo_root)
            self.assertFalse(result["allowed"])
            self.assertEqual(result["reason"], "cross_microverso_write_blocked")

    def test_guard_write_fails_without_active_microverso(self):
        with tempfile.TemporaryDirectory() as td:
            acervo_root = Path(td) / "acervo"
            target = acervo_root / "micro" / "ensino" / "knowledge" / "nota.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            with self.assertRaises(RuntimeError):
                guard_write_path(target, active_microverso=None, acervo_root=acervo_root, cwd=Path(td))

    def test_resolve_active_microverso_from_cwd(self):
        with tempfile.TemporaryDirectory() as td:
            acervo_root = Path(td) / "acervo"
            cwd = acervo_root / "micro" / "estudio-criativo" / "knowledge"
            cwd.mkdir(parents=True, exist_ok=True)
            slug = resolve_active_microverso(cwd=cwd, acervo_root=acervo_root)
            self.assertEqual(slug, "estudio-criativo")


if __name__ == "__main__":
    unittest.main()
