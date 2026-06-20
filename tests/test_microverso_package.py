"""Round-trip test: export a fixture microverso, import it into a clean acervo."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS = REPO_ROOT / "acervo" / "global" / "tools"
PACKAGE = TOOLS / "microverso_package.py"
INSTALL = TOOLS / "microverso_install.py"
VALIDATOR = REPO_ROOT / "scripts" / "validate_frontmatter.py"

INDEX_MD = """---
type: context
title: Index
description: Fixture microverso index.
tags: [test]
timestamp: 2026-06-01
class: perene
created_at: 2026-06-01T00:00:00Z
---

# Index
"""

FACT_MD = """---
type: knowledge
title: Test fact
description: A fact referencing excrtx-test-skill.
tags: [test]
timestamp: 2026-06-01
class: volátil
created_at: 2026-06-01T00:00:00Z
last_accessed_at: 2026-06-03T00:00:00Z
---

Uses excrtx-test-skill for something.
"""

OLD_MD = """---
type: knowledge
title: Old fact
description: Superseded fact.
tags: [test]
timestamp: 2026-06-01
class: volátil
created_at: 2026-06-01T00:00:00Z
deprecated: true
deprecated_at: 2026-06-02T00:00:00Z
deprecated_reason: superseded by fact.md
---

old.
"""

SKILL_MD = """---
name: excrtx-test-skill
description: Test skill for round-trip.
version: 1.0.0
---
# Test Skill
"""


def make_fixture(acervo, hermes, slug="fix-mv"):
    micro = acervo / "micro" / slug
    (micro / "_meta").mkdir(parents=True)
    (micro / "knowledge").mkdir(parents=True)
    (micro / "_meta" / "index.md").write_text(INDEX_MD, encoding="utf-8")
    (micro / "knowledge" / "fact.md").write_text(FACT_MD, encoding="utf-8")
    (micro / "knowledge" / "old.md").write_text(OLD_MD, encoding="utf-8")
    skill = hermes / "skills" / "excrtx" / "excrtx-test-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(SKILL_MD, encoding="utf-8")


def run(cmd, **env):
    full = dict(os.environ)
    full.update({"EXOCORTEX_REPO": str(REPO_ROOT)})
    full.update(env)
    return subprocess.run([sys.executable, *cmd], capture_output=True, text=True, env=full)


class RoundTripTest(unittest.TestCase):
    def test_export_then_import(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            src_acervo = tmp / "src"
            src_hermes = tmp / "hermes-src"
            out = tmp / "out"
            make_fixture(src_acervo, src_hermes)

            # export
            r = run([str(PACKAGE), "--microverso", "fix-mv", "--acervo", str(src_acervo),
                     "--out", str(out), "--tar", "--version", "1.0.0"],
                    HERMES_HOME=str(src_hermes))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            tarball = out / "fix-mv-v1.0.0.mvpkg.tar.gz"
            self.assertTrue(tarball.is_file())

            pkg = out / "fix-mv-v1.0.0.mvpkg"
            # last_accessed_at stripped from packaged content
            fact = (pkg / "acervo" / "knowledge" / "fact.md").read_text(encoding="utf-8")
            self.assertNotIn("last_accessed_at", fact)
            # deprecated file dropped
            self.assertFalse((pkg / "acervo" / "knowledge" / "old.md").exists())
            # referenced skill bundled
            self.assertTrue((pkg / "skills" / "excrtx-test-skill" / "SKILL.md").is_file())
            # packaged content passes OKF
            v = subprocess.run([sys.executable, str(VALIDATOR), "--dir", str(pkg / "acervo")],
                               capture_output=True, text=True)
            self.assertEqual(v.returncode, 0, v.stdout + v.stderr)

            # import into clean acervo + hermes
            dst_acervo = tmp / "dst"
            dst_hermes = tmp / "hermes-dst"
            r2 = run([str(INSTALL), str(tarball), "--acervo", str(dst_acervo)],
                     HERMES_HOME=str(dst_hermes))
            self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
            self.assertIn("integrity: OK", r2.stdout)

            installed = dst_acervo / "micro" / "fix-mv"
            self.assertTrue((installed / "knowledge" / "fact.md").is_file())
            self.assertTrue((installed / "microverso.yaml").is_file())
            # skill installed into target hermes
            self.assertTrue(
                (dst_hermes / "skills" / "excrtx" / "excrtx-test-skill" / "SKILL.md").is_file())
            # registered in global manifest
            reg = (dst_acervo / "global" / "_meta" / "microversos.yaml").read_text(encoding="utf-8")
            self.assertIn("fix-mv", reg)


if __name__ == "__main__":
    unittest.main()
