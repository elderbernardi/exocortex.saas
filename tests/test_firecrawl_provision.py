#!/usr/bin/env python3
import os
import subprocess
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
STEP_TIER_TEST = REPO / "tests" / "test_step11c_firecrawl_tiers.sh"
SMOKE = REPO / "provision" / "firecrawl" / "scripts" / "smoke.sh"
HERMES_HOME = Path.home() / ".hermes"
FIRECRAWL_DIR = HERMES_HOME / "firecrawl"


class FirecrawlProvisionTest(unittest.TestCase):
    def test_step11c_shell_suite_passes(self):
        result = subprocess.run(
            ["bash", str(STEP_TIER_TEST)],
            cwd=str(REPO),
            capture_output=True,
            text=True,
            timeout=180,
        )
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        self.assertIn("All tests passed.", result.stdout)

    def test_smoke_script_passes_against_live_runtime(self):
        env = os.environ.copy()
        env["HERMES_HOME"] = str(HERMES_HOME)
        env["EXOCORTEX_FIRECRAWL_DIR"] = str(FIRECRAWL_DIR)
        env["FIRECRAWL_BASE_URL"] = env.get("FIRECRAWL_BASE_URL", "http://127.0.0.1:3002")

        result = subprocess.run(
            ["bash", str(SMOKE)],
            cwd=str(REPO),
            env=env,
            capture_output=True,
            text=True,
            timeout=180,
        )
        self.assertEqual(result.returncode, 0, result.stdout + "\n" + result.stderr)
        self.assertIn("Smoke test Firecrawl concluído.", result.stdout)


if __name__ == "__main__":
    unittest.main()
