#!/usr/bin/env python3
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

GLOBAL_FILES = [
    "acervo/global/decisions/adr-019-memory-operating-model.md",
    "acervo/global/decisions/adr-020-acervo-hindsight-index.md",
    "acervo/global/decisions/adr-021-memory-fast-layer-budget.md",
    "acervo/global/contracts/memory-routing-contract.md",
    "acervo/global/tools/acervo-hindsight-indexer-spec.md",
    "acervo/global/reflections/memory-architecture-brainstorm-2026-06-21.md",
]

OPS_FILES = [
    "acervo/micro/exocortex-ops/workflows/memory-excellence-execution-plan.md",
    "acervo/micro/exocortex-ops/workflows/installer-memory-improvements-task.md",
    "acervo/micro/exocortex-ops/context/memory-excellence-progress.md",
    "acervo/micro/exocortex-ops/context/memory-excellence-handoff-log.md",
]


class MemoryCanonicalizationTest(unittest.TestCase):
    def test_memory_architecture_seed_is_canonical_not_dev_only(self):
        for rel in GLOBAL_FILES + OPS_FILES:
            with self.subTest(path=rel):
                self.assertTrue((REPO / rel).exists(), rel)

    def test_installer_scans_canonical_acervo_not_exocortex_dev_only(self):
        setup = (REPO / "setup.sh").read_text(encoding="utf-8")
        self.assertIn("--scan-global", setup)
        self.assertIn("--skip-micro-scan", setup)
        self.assertNotIn("--microverso exocortex-dev \\", setup)

        smoke = (REPO / "setup" / "step-13-final-verification.sh").read_text(encoding="utf-8")
        self.assertIn("--scan-global", smoke)
        self.assertIn("--skip-micro-scan", smoke)
        self.assertNotIn("--microverso exocortex-dev", smoke)

    def test_global_index_exposes_memory_contracts(self):
        index = (REPO / "acervo" / "global" / "_meta" / "index.md").read_text(encoding="utf-8")
        for rel in GLOBAL_FILES:
            self.assertIn(Path(rel).name, index)


if __name__ == "__main__":
    unittest.main()
