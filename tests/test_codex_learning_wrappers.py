#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CodexLearningWrappersTest(unittest.TestCase):
    @staticmethod
    def _repo_root() -> Path:
        return Path(__file__).resolve().parents[1]

    def test_runner_smoke_creates_summary_and_reviewer_reads_it(self):
        repo_root = self._repo_root()
        runner = repo_root / "scripts" / "codex_learning" / "run_codex_with_learning.py"
        reviewer = repo_root / "scripts" / "codex_learning" / "review_latest_run.py"

        with tempfile.TemporaryDirectory() as td:
            hermes_home = Path(td) / "hermes-home"
            env = os.environ.copy()
            env["HERMES_HOME"] = str(hermes_home)

            run = subprocess.run(
                [
                    sys.executable,
                    str(runner),
                    "--scratch",
                    "--prompt",
                    "Crie apenas evidência de smoke.",
                    "--simulate-output",
                    "OK",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                env=env,
                cwd=repo_root,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            payload = json.loads(run.stdout)
            summary_path = Path(payload["summary_path"])
            self.assertTrue(summary_path.is_file())
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["exit_code"], 0)
            self.assertEqual(summary["stdout"], "OK")
            self.assertTrue(summary["scratch"])
            self.assertTrue((hermes_home / "codex-learning" / "events").is_dir())

            review = subprocess.run(
                [sys.executable, str(reviewer), "--run-id", summary["run_id"]],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                env=env,
                cwd=repo_root,
            )
            self.assertEqual(review.returncode, 0, review.stderr)
            review_payload = json.loads(review.stdout)
            review_path = Path(review_payload["review_path"])
            self.assertTrue(review_path.is_file())
            review_text = review_path.read_text(encoding="utf-8")
            self.assertIn(summary["run_id"], review_text)
            self.assertIn("OK", review_text)


if __name__ == "__main__":
    unittest.main()
