#!/usr/bin/env python3
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
LOCK_FILE = REPO_ROOT / "provision" / "sources" / "sources.lock.yaml"
SYNC_SCRIPT = REPO_ROOT / "provision" / "sources" / "sync-upstreams.sh"


class ControlledSourcesTest(unittest.TestCase):
    def test_sources_lock_uses_pinned_audited_refs(self):
        content = LOCK_FILE.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        sources = data["sources"]

        self.assertIn("owner_repo: NousResearch/hermes-agent", content)
        self.assertIn("spdx: MIT", content)
        for name, source in sources.items():
            ref = source["controlled"]["ref"]
            if name == "hermes-webui" and source["controlled"]["git"] == "pending-controlled-fork":
                self.assertIn(ref, ("master", "main"))
            else:
                self.assertRegex(ref, r"^[0-9a-f]{40}$")
                self.assertNotIn(ref, ("main", "master", "HEAD", "pending-controlled-pin"))

    def test_sync_script_dry_run_does_not_create_workspace(self):
        with tempfile.TemporaryDirectory() as td:
            workspace = Path(td) / "worktrees"
            run = subprocess.run(
                ["bash", str(SYNC_SCRIPT), "--workspace", str(workspace), "--source", "hermes-agent"],
                cwd=REPO_ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertIn("Modo: dry-run", run.stdout)
            self.assertFalse(workspace.exists())

    def test_no_bsl_licensed_sources_remain(self):
        """Ensure no source is licensed under BSL."""
        data = yaml.safe_load(LOCK_FILE.read_text(encoding="utf-8"))
        sources = data["sources"]
        for name, source in sources.items():
            license_info = source.get("license", {})
            spdx = license_info.get("spdx", "")
            license_name = license_info.get("name", "")
            self.assertNotIn("BSL", spdx, f"{name} uses BSL license (spdx)")
            self.assertNotIn("BSL", license_name, f"{name} uses BSL license (name)")
            self.assertFalse(
                license_info.get("commercial_use_requires_license", False),
                f"{name} requires commercial license",
            )

    def test_hermes_webui_registered_with_mit_license(self):
        """Verify hermes-webui is registered as MIT-licensed source."""
        content = LOCK_FILE.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        sources = data["sources"]

        self.assertIn("hermes-webui", sources)
        webui = sources["hermes-webui"]
        self.assertEqual(webui["upstream"]["owner_repo"], "nesquena/hermes-webui")
        self.assertEqual(webui["license"]["spdx"], "MIT")
        self.assertFalse(webui["license"]["commercial_use_requires_license"])
        self.assertRegex(webui["controlled"]["ref"], r"^([0-9a-f]{40}|master|main)$")

    def test_sync_script_dry_run_hermes_webui(self):
        """Verify sync script recognizes hermes-webui source."""
        with tempfile.TemporaryDirectory() as td:
            workspace = Path(td) / "worktrees"
            run = subprocess.run(
                ["bash", str(SYNC_SCRIPT), "--workspace", str(workspace), "--source", "hermes-webui"],
                cwd=REPO_ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertIn("hermes-webui", run.stdout)
            self.assertIn("nesquena/hermes-webui", run.stdout)

    def test_webui_install_script_exists(self):
        """Verify the hermes-webui install script exists."""
        installer = REPO_ROOT / "provision" / "hermes-webui" / "scripts" / "install.sh"
        self.assertTrue(installer.exists(), f"Install script missing: {installer}")


if __name__ == "__main__":
    unittest.main()
