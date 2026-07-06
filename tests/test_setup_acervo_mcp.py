#!/usr/bin/env python3
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
STEP = REPO / "setup" / "step-11b-integration-acervo-mcp.sh"
FINAL_VERIFICATION = REPO / "setup" / "step-13-final-verification.sh"
SERVER_SCRIPT = REPO / "scripts" / "acervo_mcp_server.py"


class SetupAcervoMcpTest(unittest.TestCase):
    def _base_env(self, hermes_home: Path, exocortex_home: Path, acervo_root: Path) -> dict[str, str]:
        env = os.environ.copy()
        # Neutralize any ambient BASH_ENV (e.g. a dev shell that auto-loads a
        # ~/.env.local into every subshell). It would re-export the real
        # HERMES_HOME over our isolated one after the step starts, silently
        # redirecting the step's config write to the real ~/.hermes.
        env["BASH_ENV"] = ""
        env["HERMES_HOME"] = str(hermes_home)
        env["EXOCORTEX_HOME"] = str(exocortex_home)
        env["ACERVO"] = str(acervo_root)
        return env

    @unittest.skipUnless(shutil.which("hermes"), "requires the hermes CLI on PATH")
    def test_step_registers_acervo_mcp_idempotently(self):
        with tempfile.TemporaryDirectory() as td:
            isolated = Path(td)
            hermes_home = isolated / ".hermes"
            exocortex_home = isolated / "exocortex"
            acervo_root = exocortex_home / "acervo"
            hermes_home.mkdir(parents=True)
            acervo_root.mkdir(parents=True)

            env = self._base_env(hermes_home, exocortex_home, acervo_root)

            first = subprocess.run(
                ["bash", str(STEP)],
                cwd=str(REPO),
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(first.returncode, 0, first.stdout + "\n" + first.stderr)
            self.assertIn("MCP server 'acervo' registrado e saudável", first.stdout)

            config_path = hermes_home / "config.yaml"
            self.assertTrue(config_path.exists())
            cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
            acervo_cfg = cfg["mcp_servers"]["acervo"]
            self.assertEqual(acervo_cfg["command"], shutil.which("python3"))
            self.assertEqual(acervo_cfg["args"], [str(SERVER_SCRIPT)])
            self.assertEqual(acervo_cfg["env"]["ACERVO"], str(acervo_root))
            self.assertEqual(acervo_cfg["env"]["EXOCORTEX_HOME"], str(exocortex_home))
            self.assertEqual(acervo_cfg["env"]["HERMES_HOME"], str(hermes_home))
            self.assertTrue(acervo_cfg["enabled"])

            health = subprocess.run(
                ["hermes", "mcp", "test", "acervo"],
                cwd=str(REPO),
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(health.returncode, 0, health.stdout + "\n" + health.stderr)

            second = subprocess.run(
                ["bash", str(STEP)],
                cwd=str(REPO),
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(second.returncode, 0, second.stdout + "\n" + second.stderr)
            self.assertIn("já configurado", second.stdout)

            cfg_after = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
            self.assertIn("acervo", cfg_after.get("mcp_servers", {}))
            self.assertEqual(cfg_after["mcp_servers"]["acervo"]["args"], [str(SERVER_SCRIPT)])

    def test_setup_and_final_verification_wire_acervo_mcp(self):
        setup_text = (REPO / "setup.sh").read_text(encoding="utf-8")
        self.assertIn('step-11b-integration-acervo-mcp.sh', setup_text)

        final_text = FINAL_VERIFICATION.read_text(encoding="utf-8")
        self.assertIn('Acervo MCP (registro + health):', final_text)
        self.assertIn('hermes mcp test acervo', final_text)
        self.assertIn('acervo_mcp_server.py" --self-test', final_text)
        self.assertIn("MCP server 'acervo' registrado", final_text)


if __name__ == "__main__":
    unittest.main()
