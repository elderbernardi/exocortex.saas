#!/usr/bin/env python3
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
LOCK_FILE = REPO_ROOT / "provision" / "sources" / "sources.lock.yaml"
SYNC_SCRIPT = REPO_ROOT / "provision" / "sources" / "sync-upstreams.sh"
COMMON_SCRIPT = REPO_ROOT / "provision" / "hermes-web-ui" / "scripts" / "common.sh"


class ControlledSourcesTest(unittest.TestCase):
    def test_sources_lock_uses_pinned_audited_refs(self):
        content = LOCK_FILE.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        sources = data["sources"]

        self.assertIn("owner_repo: NousResearch/hermes-agent", content)
        self.assertIn("spdx: MIT", content)
        self.assertIn("owner_repo: EKKOLearnAI/hermes-web-ui", content)
        self.assertIn("observed_redirect: EKKOLearnAI/hermes-studio", content)
        self.assertIn("name: BSL 1.1", content)
        self.assertIn("commercial_use_requires_license: true", content)
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

    def test_common_resolves_web_ui_repo_and_ref_from_sources_lock_when_env_is_blank(self):
        with tempfile.TemporaryDirectory() as td:
            env_file = Path(td) / ".env"
            env_file.write_text(
                "EXOCORTEX_HERMES_WEB_UI_REPO_URL=\n"
                "EXOCORTEX_HERMES_WEB_UI_REF=\n"
                "AUTH_JWT_SECRET=test-secret\n"
                "EXOCORTEX_ADMIN_PASSWORD=test-password\n",
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["EXOCORTEX_PROVISION_ENV_FILE"] = str(env_file)
            run = subprocess.run(
                [
                    "bash",
                    "-lc",
                    f'source "{COMMON_SCRIPT}" && load_env && printf "%s\\n%s\\n" "$EXOCORTEX_HERMES_WEB_UI_REPO_URL" "$EXOCORTEX_HERMES_WEB_UI_REF"',
                ],
                cwd=REPO_ROOT,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            lines = [
                line
                for line in run.stdout.strip().splitlines()
                if line.startswith("https://") or line.isalnum()
            ]
            self.assertEqual(lines[0], "https://github.com/EKKOLearnAI/hermes-web-ui.git")
            self.assertRegex(lines[1], r"^[0-9a-f]{40}$")


if __name__ == "__main__":
    unittest.main()
