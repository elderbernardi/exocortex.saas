#!/usr/bin/env python3
"""Tests for runtime enforcement helpers introduced by issue #56."""

import tempfile
import unittest
from pathlib import Path

import os
from unittest import mock

from scripts.exocortex_runtime_guard import (
    _resolve_acervo_root,
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


class AcervoRootResolutionTest(unittest.TestCase):
    """Regression: the guard must resolve the live Acervo from the environment,
    not from its own script location (installer clone)."""

    def test_acervo_env_takes_precedence(self):
        with mock.patch.dict(os.environ, {"ACERVO": "/srv/exocortex/acervo"}, clear=False):
            self.assertEqual(_resolve_acervo_root(), Path("/srv/exocortex/acervo"))

    def test_exocortex_home_when_dir_exists(self):
        with tempfile.TemporaryDirectory() as td:
            acervo = Path(td) / "acervo"
            acervo.mkdir(parents=True)
            env = {k: v for k, v in os.environ.items() if k not in {"ACERVO"}}
            env["EXOCORTEX_HOME"] = td
            with mock.patch.dict(os.environ, env, clear=True):
                self.assertEqual(_resolve_acervo_root(), acervo)

    def test_write_not_blocked_when_cwd_differs_from_acervo(self):
        # Reproduces the EX-11 smoke failure: guard invoked from the installer
        # clone (cwd) but writing to the live Acervo via $ACERVO.
        with tempfile.TemporaryDirectory() as live, tempfile.TemporaryDirectory() as installer:
            acervo_root = Path(live) / "acervo"
            target = acervo_root / "micro" / "estudio-criativo" / "knowledge" / "nota.md"
            target.parent.mkdir(parents=True)
            result = guard_write_path(
                target,
                active_microverso="estudio-criativo",
                acervo_root=acervo_root,
                cwd=Path(installer),
            )
            self.assertTrue(result["allowed"])
            self.assertEqual(result["reason"], "within_active_microverso")


if __name__ == "__main__":
    unittest.main()
