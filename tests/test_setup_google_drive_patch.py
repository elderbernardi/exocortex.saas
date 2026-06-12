#!/usr/bin/env python3
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class SetupGoogleDrivePatchTest(unittest.TestCase):
    @staticmethod
    def _patch_script() -> str:
        patch_path = Path(__file__).resolve().parents[1] / "setup" / "step-06-hardening.sh"
        patch_text = patch_path.read_text(encoding="utf-8")
        match = re.search(r"python3 - \"\$gapi\" <<'PY'\n(.*?)\nPY", patch_text, re.DOTALL)
        if match is None:
            raise AssertionError("python patch block not found in setup/step-06-hardening.sh")
        return match.group(1)

    @staticmethod
    def _run_patch(script: str, target: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-", str(target)],
            input=script,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    @staticmethod
    def _compile(target: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "py_compile", str(target)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_embedded_patch_produces_compilable_google_api(self):
        patch_script = self._patch_script()
        sample = """import json
import sys


def _gws_binary():
    return False


def build_service(*_args, **_kwargs):
    raise NotImplementedError


def drive_search(args):
    print('old implementation')


def drive_get(args):
    return None
"""

        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "google_api.py"
            target.write_text(sample, encoding="utf-8")

            first_run = self._run_patch(patch_script, target)
            self.assertEqual(first_run.returncode, 0, first_run.stderr)
            self.assertEqual(first_run.stdout.strip(), "PATCHED")

            patched = target.read_text(encoding="utf-8")
            self.assertIn("trashed = false", patched)
            self.assertIn("nextPageToken, files(", patched)

            compile_run = self._compile(target)
            self.assertEqual(compile_run.returncode, 0, compile_run.stderr)

            second_run = self._run_patch(patch_script, target)
            self.assertEqual(second_run.returncode, 0, second_run.stderr)
            self.assertEqual(second_run.stdout.strip(), "ALREADY")
            self.assertEqual(target.read_text(encoding="utf-8"), patched)

    def test_patch_does_not_false_positive_on_marker_substrings_elsewhere(self):
        patch_script = self._patch_script()
        sample = """import json
import sys

MARKERS = ["trashed = false", "nextPageToken, files("]


def _gws_binary():
    return False


def build_service(*_args, **_kwargs):
    raise NotImplementedError


def drive_search(args):
    print('old implementation')


def drive_get(args):
    return None
"""

        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "google_api.py"
            target.write_text(sample, encoding="utf-8")

            result = self._run_patch(patch_script, target)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "PATCHED")
            self.assertEqual(self._compile(target).returncode, 0)

    def test_unchanged_invalid_file_is_not_reported_as_patched(self):
        patch_script = self._patch_script()
        sample = """import json
import sys


def _gws_binary():
    return False


def build_service(*_args, **_kwargs):
    raise NotImplementedError


def drive_search(args):
    if args.max < 1:
        print("ERROR: --max must be >= 1", file=sys.stderr)
        sys.exit(1)

    if args.raw_query:
        query = args.query
    else:
        # Escape single quotes in Drive query literals and ignore trashed items by default.
        escaped = args.query.replace('\\\\', '\\\\\\\\').replace("'", "\\\\'")
        query = f"fullText contains '{escaped}' and trashed = false"

    fields = "nextPageToken, files(id, name, mimeType, modifiedTime, webViewLink)"
    page_size = min(args.max, 1000)
    files = []
    page_token = None

    if _gws_binary():
        while len(files) < args.max:
            params = {
                "q": query,
                "pageSize": min(page_size, args.max - len(files)),
                "fields": fields,
            }
            if page_token:
                params["pageToken"] = page_token
            results = _run_gws(["drive", "files", "list"], params=params)
            files.extend(results.get("files", []))
            page_token = results.get("nextPageToken")
            if not page_token:
                break
        print(json.dumps(files[: args.max], indent=2, ensure_ascii=False))
        return

    service = build_service("drive", "v3")
    while len(files) < args.max:
        results = service.files().list(
            q=query,
            pageSize=min(page_size, args.max - len(files)),
            fields=fields,
            pageToken=page_token,
        ).execute()
        files.extend(results.get("files", []))
        page_token = results.get("nextPageToken")
        if not page_token:
            break
    print(json.dumps(files[: args.max], indent=2, ensure_ascii=False))


def drive_get(args):
    return None


def broken_tail(:
    return None
"""

        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "google_api.py"
            target.write_text(sample, encoding="utf-8")

            result = self._run_patch(patch_script, target)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "SKIP")
            self.assertNotEqual(self._compile(target).returncode, 0)


if __name__ == "__main__":
    unittest.main()
