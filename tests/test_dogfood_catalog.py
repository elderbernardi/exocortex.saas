#!/usr/bin/env python3
import tempfile
import unittest
from pathlib import Path

from scripts.dogfood_validate_catalog import extract_feature_ids, validate_catalog


class DogfoodCatalogTest(unittest.TestCase):
    def test_extract_feature_ids_from_features_md(self):
        text = """
        ### EX-01. Welcome
        text
        ### EX-35. Surfaces
        """
        self.assertEqual(extract_feature_ids(text), ["EX-01", "EX-35"])

    def test_catalog_fails_when_required_scenario_is_missing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            features = root / "FEATURES.md"
            features.write_text("### EX-08. Draft-First\n", encoding="utf-8")
            (root / ".dogfood" / "scenarios").mkdir(parents=True)

            result = validate_catalog(root, required_ids=["EX-08"])

            self.assertFalse(result.ok)
            self.assertIn("EX-08", result.missing_scenarios)

    def test_catalog_passes_when_required_scenario_exists(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            features = root / "FEATURES.md"
            features.write_text("### EX-08. Draft-First\n", encoding="utf-8")
            scenario_dir = root / ".dogfood" / "scenarios"
            scenario_dir.mkdir(parents=True)
            (scenario_dir / "EX-08.yaml").write_text(
                "feature_id: EX-08\ntitle: Draft First\ncategory: Behavior\nsource: FEATURES.md\nrisk: P0\nmode: conversational\nuser_prompt: |\n  Envie uma mensagem.\nsuccess_criteria:\n  - gera DRAFT\nfailure_signals:\n  - send_message\nevidence_required:\n  - transcript\n",
                encoding="utf-8",
            )

            result = validate_catalog(root, required_ids=["EX-08"])

            self.assertTrue(result.ok, result.errors)


if __name__ == "__main__":
    unittest.main()
