from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
STEP = REPO / "setup" / "step-03-install-skills.sh"


EXPECTED_LINKED_FILES = (
    Path("excrtx-brandkit-generator/references/editorial-book-cover-from-technical-brand.md"),
    Path("excrtx-quality-taste/references/editorial-book-cover-preflight.md"),
    Path("excrtx-quality-taste/templates/brutalist-report.html"),
    Path("excrtx-produce-artifacts/references/full-wrap-editorial-artifact.md"),
)


def test_step_install_skills_copies_linked_files_recursively() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        hermes_home = root / "hermes"
        exocortex_home = root / "exocortex"
        acervo = exocortex_home / "acervo"

        env = os.environ.copy()
        env.update(
            {
                "HERMES_HOME": str(hermes_home),
                "EXOCORTEX_HOME": str(exocortex_home),
                "ACERVO": str(acervo),
            }
        )

        result = subprocess.run(
            ["bash", str(STEP)],
            cwd=REPO,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, result.stdout + "\n" + result.stderr

        source_root = REPO / "skills"
        installed_root = hermes_home / "skills" / "excrtx"

        for relative_path in EXPECTED_LINKED_FILES:
            source = source_root / relative_path
            installed = installed_root / relative_path
            assert source.is_file(), f"missing source fixture: {source}"
            assert installed.is_file(), f"installer omitted linked file: {installed}"
            assert installed.read_bytes() == source.read_bytes()


def test_step_install_skills_preserves_hidden_skill_files() -> None:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        source_root = root / "source"
        target_root = root / "target"
        skill = source_root / "fixture-skill"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: fixture-skill\ndescription: fixture\n---\nbody\n")
        hidden = skill / ".skill-metadata"
        hidden.write_text("preserve me\n")

        env = os.environ.copy()
        env.update(
            {
                "TEST_SKILLS_SRC": str(source_root),
                "TEST_SKILLS_DST": str(target_root),
                "HERMES_HOME": str(root / "hermes"),
                "EXOCORTEX_HOME": str(root / "exocortex"),
                "ACERVO": str(root / "exocortex" / "acervo"),
            }
        )

        command = (
            'source setup/common.sh; '
            'SKILLS_SRC="$TEST_SKILLS_SRC"; '
            'SKILLS_DST="$TEST_SKILLS_DST"; '
            'source setup/step-03-install-skills.sh'
        )
        result = subprocess.run(
            ["bash", "-c", command],
            cwd=REPO,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, result.stdout + "\n" + result.stderr
        installed_hidden = target_root / "fixture-skill" / hidden.name
        assert installed_hidden.read_bytes() == hidden.read_bytes()
