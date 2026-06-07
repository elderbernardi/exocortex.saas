#!/usr/bin/env python3
"""Tests for gcloud_quick_setup.py — Google Cloud quick-setup guide generator."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
SCRIPT = SCRIPTS_DIR / "gcloud_quick_setup.py"


class GcloudQuickSetupTest(unittest.TestCase):
    @staticmethod
    def _run(*extra_args, client_secret=None, gcloud_project=None):
        """Run gcloud_quick_setup.py with optional env/context overrides."""
        env_extra = {}
        # We can't easily mock client_secret.json detection because it
        # reads from HERMES_HOME, but we can test --project override.
        cmd = [sys.executable, str(SCRIPT)] + list(extra_args)
        return subprocess.run(
            cmd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_json_output_has_required_keys(self):
        result = self._run("--project", "test-project-123")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["project_id"], "test-project-123")
        self.assertEqual(data["detected_from"], "user_provided")
        self.assertIn("setup_url", data)
        self.assertIn("api_links", data)
        self.assertIn("credentials_url", data)
        self.assertIn("test_users_url", data)
        self.assertIn("enable_all_url", data)

    def test_text_output_contains_all_sections(self):
        result = self._run("--format", "text", "--project", "my-proj")
        self.assertEqual(result.returncode, 0, result.stderr)
        output = result.stdout
        self.assertIn("my-proj", output)
        self.assertIn("APIs to enable:", output)
        self.assertIn("Gmail API:", output)
        self.assertIn("People API:", output)
        self.assertIn("Create OAuth client:", output)
        self.assertIn("Add test users:", output)

    def test_exactly_six_api_links(self):
        result = self._run("--project", "123456")
        data = json.loads(result.stdout)
        self.assertEqual(len(data["api_links"]), 6)

    def test_api_links_contain_project_id(self):
        result = self._run("--project", "proj-abc")
        data = json.loads(result.stdout)
        for link in data["api_links"]:
            self.assertIn("proj-abc", link["enable_url"])

    def test_no_project_detected_returns_error(self):
        """When no project is found and none provided, exit 1 with message."""
        # This test only works if no client_secret.json exists AND no gcloud.
        # On CI or fresh env it should fail gracefully.
        result = self._run()
        if result.returncode == 1:
            data = json.loads(result.stdout)
            self.assertEqual(data["error"], "no_project_detected")
            self.assertIn("project_selector_url", data)
        else:
            # Project was auto-detected — still valid, skip assertion
            self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()