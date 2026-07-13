#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "file_memory_eval_knowledge.py"


class FileMemoryEvalKnowledgeTest(unittest.TestCase):
    def _seed_report(self, path: Path) -> None:
        payload = {
            "run_at": "2026-07-12T18:18:54Z",
            "k": 5,
            "strategies": {
                "catalog": {
                    "overall": {
                        "n": 25,
                        "recall": 0.7955,
                        "precision": 0.347,
                        "contamination_rate": 0.0,
                        "abstention_accuracy": 0.3333,
                        "avg_token_cost": 2693,
                    }
                },
                "production": {
                    "overall": {
                        "n": 25,
                        "recall": 1.0,
                        "precision": 0.3902,
                        "contamination_rate": 0.0,
                        "abstention_accuracy": 0.6667,
                        "avg_token_cost": 2925,
                    }
                },
            },
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        path.with_suffix(".md").write_text("# fake report\n", encoding="utf-8")

    def test_materializes_knowledge_note_and_validates_it(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            acervo = base / "acervo"
            acervo.mkdir(parents=True)
            report = base / "live-2026-07-12.json"
            self._seed_report(report)

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--acervo-root",
                    str(acervo),
                    "--report-json",
                    str(report),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["ok"])

            output = Path(payload["output_path"])
            self.assertTrue(output.exists())
            text = output.read_text(encoding="utf-8")
            self.assertIn("schema: acervo/v0.2", text)
            self.assertIn("title: 'Memory eval — live (2026-07-12)'", text)
            self.assertIn("| production | 100.0% | 39.0% | 0.0% | 66.7% | 2,925 |", text)
            self.assertIn(f"`file:{report}`", text)
            self.assertIn(f"`file:{report.with_suffix('.md')}`", text)
            self.assertIn("Melhor recall: `production` = 100.0%.", text)


if __name__ == "__main__":
    unittest.main()
