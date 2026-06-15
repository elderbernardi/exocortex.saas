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
        for source in sources.values():
            ref = source["controlled"]["ref"]
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
        """Ensure no BSL-licensed components remain in the lock file."""
        content = LOCK_FILE.read_text(encoding="utf-8")
        self.assertNotIn("BSL", content)
        self.assertNotIn("EKKOLearnAI", content)
        self.assertNotIn("hermes-studio", content)
        self.assertNotIn("commercial_use_requires_license: true", content)


if __name__ == "__main__":
    unittest.main()
