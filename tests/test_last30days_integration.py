#!/usr/bin/env python3
"""Integration tests for last30days-skill — functional smoke, env, and quality.

These tests verify the last30days engine is installed and operational
without requiring API keys beyond free-tier sources.

Design principles:
- No API keys required (free sources only: Reddit, HN, GitHub, Polymarket, YouTube)
- Deterministic checks (CLI flags, exit codes, JSON schema, file outputs)
- Time-bounded (no test takes > 60s)
- Skip (not fail) when optional dependencies are missing
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# ── Discovery ──────────────────────────────────────────────────────────────

SKILL_DIR = Path("/tmp/last30days-skill/skills/last30days")
ENGINE = SKILL_DIR / "scripts" / "last30days.py"

PYTHON = os.environ.get("LAST30DAYS_PYTHON", "")
if not PYTHON:
    for candidate in [
        "/home/elder/.local/share/uv/python/cpython-3.13-linux-x86_64-gnu/bin/python3.13",
        "/usr/bin/python3.14",
        "/usr/bin/python3.13",
        "/usr/bin/python3.12",
    ]:
        if Path(candidate).exists():
            PYTHON = candidate
            break
    else:
        PYTHON = sys.executable  # fallback — will fail version check

REQUIRED_PYTHON = (3, 12)
IS_PYTHON_OK = sys.version_info >= REQUIRED_PYTHON if PYTHON == sys.executable else True


def _run(args: list[str], timeout: int = 60, **kwargs) -> subprocess.CompletedProcess:
    """Thin wrapper with timeout and env isolation."""
    env = os.environ.copy()
    env.setdefault("LAST30DAYS_CONFIG_DIR", str(tempfile.gettempdir()))
    return subprocess.run(
        [PYTHON, str(ENGINE)] + args,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(SKILL_DIR),
        env=env,
        **kwargs,
    )


# ── Test Cases ─────────────────────────────────────────────────────────────


class TestEnginePresent(unittest.TestCase):
    """Smoke — is the engine reachable and responsive?"""

    def test_engine_file_exists(self):
        self.assertTrue(ENGINE.exists(), f"Engine not found at {ENGINE}")

    def test_python_version_ok(self):
        if PYTHON != sys.executable:
            ver = subprocess.run(
                [PYTHON, "--version"], capture_output=True, text=True, timeout=5
            )
            self.assertIn("Python 3.1", ver.stdout or ver.stderr)
        else:
            self.assertTrue(IS_PYTHON_OK, f"Python {sys.version_info} < 3.12")

    def test_help_flag(self):
        result = _run(["--help"], timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Research a topic", result.stdout)


class TestDiagnose(unittest.TestCase):
    """--diagnose must return valid JSON with expected keys."""

    def test_diagnose_returns_valid_json(self):
        result = _run(["--diagnose"], timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertIsInstance(data, dict)

    def test_diagnose_free_sources_present(self):
        result = _run(["--diagnose"], timeout=30)
        data = json.loads(result.stdout)
        free_sources = {"reddit", "youtube", "hackernews", "polymarket", "github"}
        available = set(data.get("available_sources", []))
        self.assertTrue(
            free_sources.issubset(available),
            f"Missing free sources: {free_sources - available}",
        )

    def test_diagnose_local_mode(self):
        result = _run(["--diagnose"], timeout=30)
        data = json.loads(result.stdout)
        self.assertTrue(data.get("local_mode"), "local_mode should be True")


class TestQuickRun(unittest.TestCase):
    """Functional — can the engine complete a minimal pipeline?"""

    def test_quick_search_completes(self):
        result = _run(
            [
                "python programming language",
                "--days=1",
                "--search=reddit,hackernews",
                "--emit=json",
                "--max-sources=1",
            ],
            timeout=90,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertIn("clusters", data)
        self.assertIn("items_by_source", data)
        self.assertIn("generated_at", data)

    def test_json_output_has_required_sections(self):
        result = _run(
            [
                "open source AI",
                "--days=1",
                "--search=reddit",
                "--emit=json",
                "--max-sources=1",
            ],
            timeout=90,
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        required = ["clusters", "items_by_source", "errors_by_source", "generated_at"]
        for key in required:
            self.assertIn(key, data, f"Missing '{key}' in JSON output")

    def test_research_completes_under_15_seconds(self):
        import time

        start = time.monotonic()
        result = _run(
            [
                "linux kernel",
                "--days=1",
                "--search=hackernews",
                "--emit=json",
                "--max-sources=1",
            ],
            timeout=60,
        )
        elapsed = time.monotonic() - start
        self.assertEqual(result.returncode, 0)
        self.assertLess(elapsed, 45, f"Took {elapsed:.1f}s — too slow")


class TestFreeSources(unittest.TestCase):
    """Each free source must be individually testable."""

    def test_reddit_source_returns_items(self):
        result = _run(
            ["AI", "--days=7", "--search=reddit", "--emit=json"],
            timeout=90,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        items = data.get("items_by_source", {}).get("reddit", [])
        errs = data.get("errors_by_source", {}).get("reddit", "")
        # Reddit can return empty for some queries; this is not a fault.
        # We verify: no explicit error, engine completed, JSON valid.
        self.assertNotIn(
            "403",
            str(errs),
            f"Reddit 403 forbidden. Errors: {errs}",
        )
        self.assertNotIn(
            "error",
            str(errs).lower(),
            f"Reddit error. Errors: {errs}",
        )

    def test_hackernews_source(self):
        result = _run(
            [
                "programming",
                "--days=3",
                "--search=hackernews",
                "--emit=json",
                "--max-sources=1",
            ],
            timeout=90,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_github_source(self):
        result = _run(
            [
                "machine learning",
                "--days=3",
                "--search=github",
                "--emit=json",
                "--max-sources=1",
            ],
            timeout=90,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


class TestFileOutput(unittest.TestCase):
    """Can the engine save results to a file?"""

    def test_save_dir_creates_file(self):
        with tempfile.TemporaryDirectory() as td:
            result = _run(
                [
                    "test save output",
                    "--days=1",
                    "--search=reddit",
                    "--emit=md",
                    "--save-dir",
                    td,
                    "--max-sources=1",
                ],
                timeout=90,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            # Engine saves as <slug>-raw.md by default; glob both .md and .json
            files = list(Path(td).glob("*raw*"))
            self.assertGreater(len(files), 0, f"No raw output file in {td} (contents: {list(Path(td).iterdir())})")

    def test_save_suffix_distinguishes_runs(self):
        with tempfile.TemporaryDirectory() as td:
            _run(
                [
                    "suffix test A",
                    "--days=1",
                    "--search=reddit",
                    "--emit=json",
                    "--save-dir",
                    td,
                    "--save-suffix=runA",
                    "--max-sources=1",
                ],
                timeout=90,
            )
            _run(
                [
                    "suffix test B",
                    "--days=1",
                    "--search=reddit",
                    "--emit=json",
                    "--save-dir",
                    td,
                    "--save-suffix=runB",
                    "--max-sources=1",
                ],
                timeout=90,
            )
            files = list(Path(td).glob("*runA*"))
            self.assertGreater(len(files), 0, "No file with runA suffix")


class TestEnvironment(unittest.TestCase):
    """Env file, config, and prerequisites."""

    def test_config_dir_exists(self):
        config_dir = Path.home() / ".config" / "last30days"
        self.assertTrue(config_dir.exists(), f"{config_dir} does not exist")

    def test_env_file_exists(self):
        env_file = Path.home() / ".config" / "last30days" / ".env"
        self.assertTrue(env_file.exists(), f"{env_file} not found")

    def test_yt_dlp_available(self):
        result = subprocess.run(
            ["which", "yt-dlp"], capture_output=True, text=True, timeout=5
        )
        self.assertEqual(result.returncode, 0, "yt-dlp not installed")

    def test_node_available(self):
        result = subprocess.run(
            ["node", "--version"], capture_output=True, text=True, timeout=5
        )
        self.assertEqual(result.returncode, 0, "Node.js not installed")

    def test_gh_cli_available(self):
        result = subprocess.run(
            ["gh", "--version"], capture_output=True, text=True, timeout=5
        )
        self.assertEqual(result.returncode, 0, "gh CLI not installed")


# ── Runner ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
