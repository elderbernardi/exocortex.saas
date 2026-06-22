#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROVISION = REPO / "scripts" / "provision_memory_routing.py"
SMOKE = REPO / "scripts" / "smoke_memory_routing.py"


class MemoryRoutingProvisionTest(unittest.TestCase):
    def _seed_repo_root(self, root: Path) -> None:
        tool_dir = root / "acervo" / "global" / "tools"
        tool_dir.mkdir(parents=True)
        fake_index = tool_dir / "acervo_hindsight_index.py"
        fake_index.write_text(
            "#!/usr/bin/env python3\n"
            "import json, sys\n"
            "if 'scan' in sys.argv:\n"
            "    print(json.dumps({'indexed': 1, 'skipped_unchanged': 0, 'errors': 0}))\n"
            "elif 'report' in sys.argv:\n"
            "    print(json.dumps({'entries': 1, 'orphaned_manifest_entries': []}))\n"
            "else:\n"
            "    print('{}')\n",
            encoding="utf-8",
        )
        fake_index.chmod(0o755)

    def test_provision_is_idempotent_and_sets_tools_first_memory(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            hermes = base / ".hermes"
            acervo = base / "exocortex" / "acervo"
            repo_root = base / "repo"
            hermes.mkdir()
            acervo.mkdir(parents=True)
            self._seed_repo_root(repo_root)
            (hermes / "config.yaml").write_text("model:\n  default: test\n", encoding="utf-8")
            (hermes / "SOUL.md").write_text(
                "# SOUL\n\n## Self-Awareness\n\ntext\n\n<!-- COMPILED_RULES_START -->\ncompiled\n<!-- COMPILED_RULES_END -->\n",
                encoding="utf-8",
            )
            mem_dir = hermes / "memories"
            mem_dir.mkdir()
            (mem_dir / "MEMORY.md").write_text("x" * 1300, encoding="utf-8")

            cmd = [
                sys.executable, str(PROVISION),
                "--hermes-home", str(hermes),
                "--acervo", str(acervo),
                "--repo-root", str(repo_root),
                "--microverso", "exocortex-dev",
                "--consolidate-memory",
                "--json",
            ]
            first = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            self.assertEqual(first.returncode, 0, first.stderr)
            second = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            self.assertEqual(second.returncode, 0, second.stderr)

            hindsight = json.loads((hermes / "hindsight" / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(hindsight["memory_mode"], "tools")
            self.assertIs(hindsight["auto_recall"], False)
            self.assertIs(hindsight["auto_retain"], True)
            self.assertEqual(hindsight["recall_max_input_chars"], 800)

            config = (hermes / "config.yaml").read_text(encoding="utf-8")
            self.assertIn("provider: hindsight", config)
            self.assertIn("memory_enabled: true", config)
            self.assertIn("user_profile_enabled: true", config)

            soul = (hermes / "SOUL.md").read_text(encoding="utf-8")
            self.assertEqual(soul.count("## Protocolo de Memória e Contexto"), 1)
            self.assertIn("Hindsight recupera", soul)
            self.assertIn("<!-- COMPILED_RULES_START -->", soul)

            memory = (mem_dir / "MEMORY.md").read_text(encoding="utf-8")
            self.assertLess(len(memory), 1100)
            self.assertTrue((acervo / "global" / "tools" / "acervo_hindsight_index.py").exists())
            self.assertTrue((acervo / "global" / "tools" / "state" / "acervo_hindsight_index.json").exists())

    def test_smoke_accepts_deterministic_local_state(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            hermes = base / ".hermes"
            acervo = base / "exocortex" / "acervo"
            hermes.mkdir()
            (hermes / "hindsight").mkdir()
            (hermes / "hindsight" / "config.json").write_text(json.dumps({
                "memory_mode": "tools",
                "auto_recall": False,
                "auto_retain": True,
                "recall_budget": "low",
                "recall_max_input_chars": 800,
            }), encoding="utf-8")
            (hermes / "config.yaml").write_text(
                "memory:\n  provider: hindsight\n  memory_enabled: true\n  user_profile_enabled: true\n",
                encoding="utf-8",
            )
            (hermes / "SOUL.md").write_text(
                "Chame `hindsight_recall` antes de responder\nAcervo confirma\nmemória rápida só inicializa\n",
                encoding="utf-8",
            )
            (hermes / "memories").mkdir()
            (hermes / "memories" / "MEMORY.md").write_text("bootstrap", encoding="utf-8")
            tool_dir = acervo / "global" / "tools"
            tool_dir.mkdir(parents=True)
            fake = tool_dir / "acervo_hindsight_index.py"
            fake.write_text(
                "#!/usr/bin/env python3\n"
                "import json, sys\n"
                "print(json.dumps({'errors': 0, 'entries': 1}))\n",
                encoding="utf-8",
            )
            fake.chmod(0o755)

            result = subprocess.run([
                sys.executable, str(SMOKE),
                "--hermes-home", str(hermes),
                "--acervo", str(acervo),
            ], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            data = json.loads(result.stdout)
            self.assertTrue(data["ok"])


if __name__ == "__main__":
    unittest.main()
