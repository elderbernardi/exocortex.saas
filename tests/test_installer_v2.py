from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


installer = _load_module("exocortex_install_test", SCRIPTS / "exocortex_install.py")
behavior = _load_module("verify_exocortex_behavior_test", SCRIPTS / "verify_exocortex_behavior.py")
SCENARIOS = behavior.SCENARIOS
evaluate = behavior.evaluate


def _write_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def test_profiles_are_explicit_and_full_includes_self_hosted_services() -> None:
    core_ids = [stage.id for stage in installer.selected_stages("core")]
    full_ids = [stage.id for stage in installer.selected_stages("full")]

    assert "hindsight" not in core_ids
    assert "firecrawl" not in core_ids
    assert "webui" not in core_ids
    assert {"hindsight", "firecrawl", "webui"}.issubset(full_ids)
    assert "verify" in core_ids
    assert "verify" in full_ids


def test_preflight_requires_existing_configured_hermes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for command in ("python3", "git", "rsync", "bash"):
        target = Path(os.environ.get(f"TEST_{command.upper()}_BIN", "")) if os.environ.get(f"TEST_{command.upper()}_BIN") else None
        resolved = target if target and target.exists() else Path(subprocess.check_output(["sh", "-c", f"command -v {command}"], text=True).strip())
        (bin_dir / command).symlink_to(resolved)
    _write_executable(
        bin_dir / "hermes",
        "#!/usr/bin/env bash\n"
        "if [ \"${1:-}\" = config ] && [ \"${2:-}\" = check ]; then exit 0; fi\n"
        "if [ \"${1:-}\" = --version ]; then echo 'Hermes Agent v0.test'; exit 0; fi\n"
        "exit 1\n",
    )
    monkeypatch.setenv("PATH", str(bin_dir))

    result = installer.preflight("core", require_services=False)

    assert result["ok"] is True
    assert any(check["id"] == "capability:hermes-runtime" and check["status"] == "pass" for check in result["checks"])


def test_full_preflight_is_strict_about_docker_by_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for command in ("python3", "git", "rsync", "bash"):
        resolved = Path(subprocess.check_output(["sh", "-c", f"command -v {command}"], text=True).strip())
        (bin_dir / command).symlink_to(resolved)
    _write_executable(
        bin_dir / "hermes",
        "#!/usr/bin/env bash\n"
        "if [ \"${1:-}\" = config ] && [ \"${2:-}\" = check ]; then exit 0; fi\n"
        "exit 0\n",
    )
    _write_executable(bin_dir / "nlm", "#!/usr/bin/env bash\necho 'nlm version 0.7.7'\n")
    _write_executable(bin_dir / "notebooklm-mcp", "#!/usr/bin/env bash\nexit 0\n")
    monkeypatch.setenv("PATH", str(bin_dir))

    strict = installer.preflight("full", require_services=True)
    degraded = installer.preflight("full", require_services=False)

    assert strict["ok"] is False
    assert degraded["ok"] is True
    assert degraded["services_available"] is False


def test_behavior_acceptance_uses_three_high_signal_scenarios() -> None:
    assert [scenario.id for scenario in SCENARIOS] == ["identity", "evolution-vector", "draft-first"]

    identity_ok, _ = evaluate(SCENARIOS[0], "Sou o Exocórtex.IA rodando sobre o Hermes Agent.")
    evolution_ok, _ = evaluate(SCENARIOS[1], "Quem decide hoje? O que mudaria sem essa premissa?")
    draft_ok, _ = evaluate(SCENARIOS[2], "DRAFT — Para: ana@example.com\nA reunião foi confirmada.")
    draft_false_success, _ = evaluate(SCENARIOS[2], "DRAFT pronto. Mensagem enviada com sucesso.")

    assert identity_ok
    assert evolution_ok
    assert draft_ok
    assert not draft_false_success


def test_behavior_acceptance_runner_executes_exactly_three_turns(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    report = tmp_path / "behavior.json"
    calls = tmp_path / "calls.log"
    bin_dir.mkdir()
    _write_executable(
        bin_dir / "hermes",
        "#!/usr/bin/env bash\n"
        "printf '%s\\n' \"$*\" >> \"$CALLS\"\n"
        "case \"$*\" in\n"
        "  *'Quem é você'*) echo 'Sou o Exocórtex.IA rodando sobre o Hermes Agent.' ;;\n"
        "  *'centralizar todas'*) echo 'Quem sofre com a decisão? O que mudaria se a premissa fosse removida?' ;;\n"
        "  *'Envie agora'*) echo 'DRAFT — Para: ana@example.com — A reunião foi confirmada.' ;;\n"
        "  *) exit 9 ;;\n"
        "esac\n",
    )
    env = os.environ.copy()
    env.update({"PATH": f"{bin_dir}:{env['PATH']}", "CALLS": str(calls)})

    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "verify_exocortex_behavior.py"), "--json-report", str(report)],
        cwd=REPO,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert len(calls.read_text(encoding="utf-8").splitlines()) == 3
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["summary"] == {"total": 3, "passed": 3, "failed": 0}


def test_identity_step_preserves_onboarded_soul(tmp_path: Path) -> None:
    home = tmp_path / "home"
    hermes_home = home / ".hermes"
    exocortex_home = home / "exocortex"
    acervo = exocortex_home / "acervo"
    hermes_home.mkdir(parents=True)
    (acervo / "global" / "branding").mkdir(parents=True)
    soul = hermes_home / "SOUL.md"
    original = "# Identity\n\nVocê é o Exocórtex.IA — personalizada.\n\nEXECUTIVE_ONBOARDING_SENTINEL\n"
    soul.write_text(original, encoding="utf-8")

    env = os.environ.copy()
    env.update(
        {
            "HOME": str(home),
            "HERMES_HOME": str(hermes_home),
            "EXOCORTEX_HOME": str(exocortex_home),
            "ACERVO": str(acervo),
            "_EXOCORTEX_SCRIPT_DIR": str(REPO),
        }
    )
    result = subprocess.run(["bash", str(REPO / "setup" / "step-07-install-identity.sh")], env=env, text=True, capture_output=True)

    assert result.returncode == 0, result.stdout + result.stderr
    assert soul.read_text(encoding="utf-8") == original
    assert "onboarding preservados" in result.stdout


def test_identity_step_backs_up_generic_hermes_soul(tmp_path: Path) -> None:
    home = tmp_path / "home"
    hermes_home = home / ".hermes"
    exocortex_home = home / "exocortex"
    acervo = exocortex_home / "acervo"
    hermes_home.mkdir(parents=True)
    (acervo / "global" / "branding").mkdir(parents=True)
    soul = hermes_home / "SOUL.md"
    soul.write_text("# Generic Hermes personality\n", encoding="utf-8")

    env = os.environ.copy()
    env.update(
        {
            "HOME": str(home),
            "HERMES_HOME": str(hermes_home),
            "EXOCORTEX_HOME": str(exocortex_home),
            "ACERVO": str(acervo),
            "_EXOCORTEX_SCRIPT_DIR": str(REPO),
        }
    )
    result = subprocess.run(["bash", str(REPO / "setup" / "step-07-install-identity.sh")], env=env, text=True, capture_output=True)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Você é o Exocórtex.IA" in soul.read_text(encoding="utf-8")
    backups = list((hermes_home / "backups" / "exocortex-install").glob("SOUL.before-exocortex.*.md"))
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == "# Generic Hermes personality\n"


def test_public_installer_help_states_the_new_contract() -> None:
    result = subprocess.run(["bash", str(REPO / "install.sh"), "--help"], text=True, capture_output=True)

    assert result.returncode == 0
    assert "Hermes Agent já instalado" in result.stdout
    assert "--profile core|full" in result.stdout
    assert "não roda o catálogo completo de dogfood" in " ".join(result.stdout.split())


def test_bootstrap_uses_existing_hermes_and_forwards_to_checkout(tmp_path: Path) -> None:
    source = tmp_path / "source"
    bin_dir = tmp_path / "bin"
    installer_dir = tmp_path / "installer"
    capture = tmp_path / "setup-args.txt"
    source.mkdir()
    bin_dir.mkdir()
    _write_executable(
        source / "setup.sh",
        "#!/usr/bin/env bash\nprintf '%s\\n' \"$*\" > \"$CAPTURE\"\n",
    )
    subprocess.run(["git", "init", "-b", "main"], cwd=source, check=True, capture_output=True)
    subprocess.run(["git", "add", "setup.sh"], cwd=source, check=True)
    subprocess.run(
        ["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-m", "fixture"],
        cwd=source,
        check=True,
        capture_output=True,
    )
    _write_executable(
        bin_dir / "hermes",
        "#!/usr/bin/env bash\n"
        "if [ \"${1:-} ${2:-}\" = 'config check' ]; then exit 0; fi\n"
        "if [ \"${1:-}\" = --version ]; then echo 'Hermes Agent v0.test'; exit 0; fi\n"
        "exit 0\n",
    )
    env = os.environ.copy()
    env.update(
        {
            "CAPTURE": str(capture),
            "EXOCORTEX_REPO_URL": str(source),
            "EXOCORTEX_INSTALLER_DIR": str(installer_dir),
            "PATH": f"{bin_dir}:{env['PATH']}",
            "VERSION": "main",
        }
    )

    result = subprocess.run(
        ["bash", str(REPO / "install.sh"), "--profile", "core", "--plan"],
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert capture.read_text(encoding="utf-8").strip() == "--profile core --plan"
    assert (installer_dir / ".git").is_dir()


def test_core_apply_is_idempotent_over_existing_hermes(tmp_path: Path) -> None:
    home = tmp_path / "home"
    hermes_home = home / ".hermes"
    exocortex_home = home / "exocortex"
    bin_dir = tmp_path / "bin"
    hermes_home.mkdir(parents=True)
    bin_dir.mkdir()
    marker = hermes_home / "operator-owned.txt"
    marker.write_text("preserve-me\n", encoding="utf-8")
    _write_executable(
        bin_dir / "hermes",
        "#!/usr/bin/env bash\n"
        "case \"${1:-} ${2:-}\" in\n"
        "  'config check') exit 0 ;;\n"
        "  'mcp list') echo 'acervo stdio healthy'; exit 0 ;;\n"
        "  'mcp add'|'mcp test') exit 0 ;;\n"
        "esac\n"
        "if [ \"${1:-}\" = --version ]; then echo 'Hermes Agent v0.test'; exit 0; fi\n"
        "exit 0\n",
    )

    env = os.environ.copy()
    env.update(
        {
            "HOME": str(home),
            "HERMES_HOME": str(hermes_home),
            "EXOCORTEX_HOME": str(exocortex_home),
            "ACERVO": str(exocortex_home / "acervo"),
            "PATH": f"{bin_dir}:{env['PATH']}",
        }
    )
    command = [
        sys.executable,
        str(SCRIPTS / "exocortex_install.py"),
        "apply",
        "--profile",
        "core",
        "--yes",
        "--acceptance",
        "skip",
    ]

    first = subprocess.run(command, cwd=REPO, env=env, text=True, capture_output=True, timeout=180)
    second = subprocess.run(command, cwd=REPO, env=env, text=True, capture_output=True, timeout=180)

    assert first.returncode == 0, first.stdout + first.stderr
    assert second.returncode == 0, second.stdout + second.stderr
    assert marker.read_text(encoding="utf-8") == "preserve-me\n"
    assert "Você é o Exocórtex.IA" in (hermes_home / "SOUL.md").read_text(encoding="utf-8")
    latest = json.loads((hermes_home / "exocortex-install" / "latest.json").read_text(encoding="utf-8"))
    assert latest["status"] == "pass"
    assert latest["profile"] == "core"
    assert all(stage["status"] == "pass" for stage in latest["results"])
