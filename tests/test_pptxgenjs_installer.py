from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parents[1]
STEP = REPO / "setup" / "step-03b-install-slide-deps.sh"
SETUP = REPO / "setup.sh"
SLIDES_SETUP = REPO / "skills" / "excrtx-produce-slides" / "scripts" / "setup-frontend-slides.sh"
SKILL_DEPS = REPO / "scripts" / "validate-skills-deps.sh"
ENV_VALIDATOR = REPO / "scripts" / "validate-environment.sh"
OUTER_INSTALLER = REPO / "install.sh"
FINAL_VERIFICATION = REPO / "setup" / "step-13-final-verification.sh"
ESTUDIO_MANIFEST = REPO / "acervo" / "micro" / "estudio-criativo" / "microverso.yaml"


def _write_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)


def test_pptxgenjs_is_wired_into_installer_contract() -> None:
    assert STEP.exists()
    assert 'step-03b-install-slide-deps.sh' in SETUP.read_text(encoding="utf-8")

    manifest = yaml.safe_load(ESTUDIO_MANIFEST.read_text(encoding="utf-8"))
    assert "pptxgenjs@4.0.1" in manifest["requires"]["node_packages"]

    skill_setup = SLIDES_SETUP.read_text(encoding="utf-8")
    assert "--install-node" in skill_setup
    assert "pptxgenjs@4.0.1" in skill_setup

    deps = SKILL_DEPS.read_text(encoding="utf-8")
    assert "pptxgenjs" in deps
    assert "npm root -g" in deps

    final_verification = FINAL_VERIFICATION.read_text(encoding="utf-8")
    assert "PptxGenJS 4.0.1" in final_verification

    combined_checks = STEP.read_text(encoding="utf-8") + skill_setup + final_verification
    assert "pptxgenjs/package.json" not in combined_checks


def test_node_and_npm_are_required_by_bootstrap() -> None:
    validator = ENV_VALIDATOR.read_text(encoding="utf-8")
    assert 'check_binary "node"    "required"' in validator
    assert 'check_binary "npm"     "required"' in validator

    installer = OUTER_INSTALLER.read_text(encoding="utf-8")
    assert "NODE_PKGS" in installer
    assert 'for cmd in git curl rsync python3 node npm; do' in installer


def test_pptxgenjs_step_installs_once_and_verifies_global_resolution(tmp_path: Path) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    npm_root = tmp_path / "npm-global" / "node_modules"
    npm_root.mkdir(parents=True)
    install_log = tmp_path / "npm-install.log"
    marker = npm_root / "pptxgenjs" / "package.json"

    _write_executable(
        fake_bin / "npm",
        f"""#!/usr/bin/env bash
set -euo pipefail
if [[ "$*" == "root -g" ]]; then
  printf '%s\\n' '{npm_root}'
  exit 0
fi
if [[ "$*" == "list -g --depth=0 pptxgenjs@4.0.1" ]]; then
  test -f '{marker}'
  exit $?
fi
if [[ "$*" == "install --global --silent pptxgenjs@4.0.1" ]]; then
  mkdir -p '{marker.parent}'
  printf '{{"name":"pptxgenjs","version":"4.0.1"}}\\n' > '{marker}'
  printf '%s\\n' "$*" >> '{install_log}'
  exit 0
fi
printf 'unexpected npm args: %s\\n' "$*" >&2
exit 9
""",
    )
    _write_executable(
        fake_bin / "node",
        f"""#!/usr/bin/env bash
set -euo pipefail
[[ "${{NODE_PATH:-}}" == *'{npm_root}'* ]]
test -f '{marker}'
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["HOME"] = str(tmp_path / "home")
    env["HERMES_HOME"] = str(tmp_path / "home" / ".hermes")

    first = subprocess.run(["bash", str(STEP)], cwd=REPO, env=env, text=True, capture_output=True)
    assert first.returncode == 0, first.stdout + first.stderr
    assert marker.exists()
    assert "PptxGenJS 4.0.1 instalado" in first.stdout

    second = subprocess.run(["bash", str(STEP)], cwd=REPO, env=env, text=True, capture_output=True)
    assert second.returncode == 0, second.stdout + second.stderr
    assert "PptxGenJS 4.0.1 já disponível" in second.stdout
    assert install_log.read_text(encoding="utf-8").splitlines() == [
        "install --global --silent pptxgenjs@4.0.1"
    ]
