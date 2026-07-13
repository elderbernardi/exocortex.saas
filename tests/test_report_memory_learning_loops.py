#!/usr/bin/env python3
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "report_memory_learning_loops.py"
FIXTURE = REPO / "tests" / "memory-eval" / "fixture" / "acervo"
TOOLS = REPO / "acervo" / "global" / "tools"
sys.path.insert(0, str(TOOLS))
import acervo_catalog  # noqa: E402


def _obj(title: str, *, created_at: str, status: str = "active", extra: str = "") -> str:
    return (
        "---\n"
        "schema: acervo/v0.2\n"
        "type: knowledge\n"
        f"title: {title}\n"
        f"description: {title}\n"
        "tags: [test]\n"
        "class: volátil\n"
        f"status: {status}\n"
        "epistemic: fact\n"
        "confidence: high\n"
        f"created_at: {created_at}\n"
        "sources: [{type: agent-inference, ref: \"acervoctl://new-object\"}]\n"
        "observed_at: 2026-07-01\n"
        "extraction: agent\n"
        f"{extra}"
        "---\n\n"
        f"# {title}\n"
    )


class ReportMemoryLearningLoopsTest(unittest.TestCase):
    def _seed_acervo(self, root: Path) -> None:
        shutil.copytree(FIXTURE, root)
        base = root / "micro" / "operacoes" / "knowledge"
        base.mkdir(parents=True, exist_ok=True)

        (base / "stable-auto.md").write_text(
            _obj("Stable auto", created_at="2026-07-05T00:00:00Z"),
            encoding="utf-8",
        )
        (base / "superseded-auto.md").write_text(
            _obj(
                "Superseded auto",
                created_at="2026-07-04T00:00:00Z",
                status="superseded",
                extra="superseded_by: micro/operacoes/knowledge/stable-auto.md\n",
            ),
            encoding="utf-8",
        )
        (base / "old-never.md").write_text(
            _obj("Old never", created_at="2025-12-20T00:00:00Z"),
            encoding="utf-8",
        )
        journal = root / "global" / "tools" / "state" / "retrieval-journal.jsonl"
        journal.parent.mkdir(parents=True, exist_ok=True)
        journal.write_text(
            json.dumps({"ts": "2026-01-01T00:00:00+00:00", "paths": []}) + "\n"
            + json.dumps({"ts": "2026-07-01T00:00:00+00:00", "paths": ["micro/operacoes/knowledge/stable-auto.md"]}) + "\n",
            encoding="utf-8",
        )
        acervo_catalog.build_catalog(root)

    def test_json_report_contains_h7_and_h12_metrics(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "acervo"
            self._seed_acervo(root)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--acervo-root",
                    str(root),
                    "--today",
                    "2026-07-12",
                    "--window-days",
                    "30",
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            payload = json.loads(proc.stdout)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["h7"]["candidate_count"], 2)
            self.assertEqual(payload["h7"]["corrected_count"], 1)
            self.assertEqual(payload["h7"]["verdict"], "tighten")
            self.assertGreaterEqual(payload["h12"]["candidate_count"], 1)
            self.assertTrue(payload["h12"]["evaluation"]["evaluated"])
            paths = {item["path"] for item in payload["h12"]["candidates"]}
            self.assertIn("micro/operacoes/knowledge/old-never.md", paths)

    def test_markdown_report_is_human_readable(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "acervo"
            self._seed_acervo(root)
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--acervo-root",
                    str(root),
                    "--today",
                    "2026-07-12",
                    "--window-days",
                    "30",
                    "--format",
                    "markdown",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertIn("## H7 — Governed auto-commit audit", proc.stdout)
            self.assertIn("Veredito: **tighten**", proc.stdout)
            self.assertIn("## H12 — Usefulness loop / use-decay", proc.stdout)
            self.assertIn("`micro/operacoes/knowledge/old-never.md`", proc.stdout)


if __name__ == "__main__":
    unittest.main()
