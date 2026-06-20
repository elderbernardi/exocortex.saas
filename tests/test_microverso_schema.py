"""Unit tests for the excrtx/v1 microverso manifest validator."""

import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "acervo" / "global" / "tools" / "microverso_schema.py"


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


schema = load_module(SCHEMA_PATH, "microverso_schema_under_test")


def valid_manifest():
    return {
        "apiVersion": "excrtx/v1",
        "kind": "Microverso",
        "metadata": {"name": "demo-mv", "version": "1.0.0", "description": "Demo"},
        "requires": {"skills": ["excrtx-quality-taste"], "python_packages": ["pkg>=1.0"]},
        "compat": {"platforms": ["linux"]},
        "tree": {"knowledge/": "facts"},
        "hooks": {"post_install": "scripts/post.sh"},
    }


class ManifestSchemaTest(unittest.TestCase):
    def test_valid_manifest_has_no_errors(self):
        issues = schema.validate_manifest(valid_manifest())
        self.assertFalse(schema.has_errors(issues), issues)

    def test_wrong_api_version_is_error(self):
        m = valid_manifest()
        m["apiVersion"] = "excrtx/v2"
        self.assertTrue(schema.has_errors(schema.validate_manifest(m)))

    def test_missing_metadata_name_is_error(self):
        m = valid_manifest()
        del m["metadata"]["name"]
        codes = {c for _s, c, _m in schema.validate_manifest(m)}
        self.assertIn("MV-011", codes)

    def test_bad_semver_is_error(self):
        m = valid_manifest()
        m["metadata"]["version"] = "1.0"
        codes = {c for _s, c, _m in schema.validate_manifest(m)}
        self.assertIn("MV-014", codes)

    def test_non_kebab_name_is_error(self):
        m = valid_manifest()
        m["metadata"]["name"] = "Demo_MV"
        codes = {c for _s, c, _m in schema.validate_manifest(m)}
        self.assertIn("MV-012", codes)

    def test_unsafe_hook_path_is_error(self):
        m = valid_manifest()
        m["hooks"]["post_install"] = "../escape.sh"
        codes = {c for _s, c, _m in schema.validate_manifest(m)}
        self.assertIn("MV-H02", codes)

    def test_skills_dict_entries_accepted(self):
        m = valid_manifest()
        m["requires"]["skills"] = [{"name": "excrtx-produce-slides", "bundled": True}]
        self.assertFalse(schema.has_errors(schema.validate_manifest(m)))

    def test_skill_without_prefix_warns_not_errors(self):
        m = valid_manifest()
        m["requires"]["skills"] = ["random-skill"]
        issues = schema.validate_manifest(m)
        self.assertFalse(schema.has_errors(issues))
        self.assertIn("MV-R04", {c for _s, c, _m in issues})


if __name__ == "__main__":
    unittest.main()
