"""Skill-collision resolution tests for the import tool (resolve_skill)."""

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INSTALL_PATH = REPO_ROOT / "acervo" / "global" / "tools" / "microverso_install.py"


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


inst = load_module(INSTALL_PATH, "microverso_install_under_test")


def make_skill(parent, name, version, body="base"):
    d = parent / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(
        f"---\nname: {name}\nversion: {version}\n---\n# {name}\n{body}\n", encoding="utf-8")
    return d


class SkillCollisionTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.src = self.tmp / "src"
        self.dst = self.tmp / "dst"
        self.src.mkdir()
        self.dst.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def test_install_when_absent(self):
        make_skill(self.src, "excrtx-x", "1.0.0")
        action, _name, _note = inst.resolve_skill("excrtx-x", self.src / "excrtx-x",
                                                  self.dst, False, False)
        self.assertEqual(action, "install")
        self.assertTrue((self.dst / "excrtx-x" / "SKILL.md").is_file())

    def test_skip_when_identical(self):
        make_skill(self.src, "excrtx-x", "1.0.0")
        make_skill(self.dst, "excrtx-x", "1.0.0")
        action, _n, _o = inst.resolve_skill("excrtx-x", self.src / "excrtx-x",
                                            self.dst, False, False)
        self.assertEqual(action, "skip")

    def test_update_pending_without_flag(self):
        make_skill(self.src, "excrtx-x", "2.0.0")
        make_skill(self.dst, "excrtx-x", "1.0.0")
        action, _n, _o = inst.resolve_skill("excrtx-x", self.src / "excrtx-x",
                                            self.dst, False, False)
        self.assertEqual(action, "update-pending")
        # existing left untouched (still 1.0.0)
        self.assertIn("version: 1.0.0", (self.dst / "excrtx-x" / "SKILL.md").read_text())

    def test_update_applied_with_flag(self):
        make_skill(self.src, "excrtx-x", "2.0.0")
        make_skill(self.dst, "excrtx-x", "1.0.0")
        action, _n, _o = inst.resolve_skill("excrtx-x", self.src / "excrtx-x",
                                            self.dst, True, False)
        self.assertEqual(action, "update")
        self.assertIn("version: 2.0.0", (self.dst / "excrtx-x" / "SKILL.md").read_text())

    def test_rename_when_divergent(self):
        make_skill(self.src, "excrtx-x", "1.0.0", body="incoming-variant")
        make_skill(self.dst, "excrtx-x", "1.0.0", body="local-variant")
        action, _n, _o = inst.resolve_skill("excrtx-x", self.src / "excrtx-x",
                                            self.dst, False, False)
        self.assertEqual(action, "rename")
        # existing kept intact (caller performs the actual rename copy)
        self.assertIn("local-variant", (self.dst / "excrtx-x" / "SKILL.md").read_text())


if __name__ == "__main__":
    unittest.main()
