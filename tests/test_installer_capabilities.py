from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).resolve().parents[1]
CHECKER = REPO / "scripts" / "check_capabilities.py"
MANIFEST = REPO / "setup" / "capabilities.json"


def _write_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


def _core_path(tmp_path: Path, *, include_git: bool = True) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for command in ("python3", "rsync", "bash"):
        target = Path(subprocess.check_output(["sh", "-c", f"command -v {command}"], text=True).strip())
        (bin_dir / command).symlink_to(target)
    if include_git:
        target = Path(subprocess.check_output(["sh", "-c", "command -v git"], text=True).strip())
        (bin_dir / "git").symlink_to(target)
    _write_executable(
        bin_dir / "hermes",
        "#!/usr/bin/env bash\n"
        "if [ \"${1:-}\" = config ] && [ \"${2:-}\" = check ]; then exit 0; fi\n"
        "if [ \"${1:-}\" = --version ]; then echo 'Hermes Agent v0.test'; exit 0; fi\n"
        "exit 1\n",
    )
    return bin_dir


def _add_docker(bin_dir: Path) -> None:
    _write_executable(
        bin_dir / "docker",
        "#!/usr/bin/env bash\n"
        "if [ \"${1:-}\" = compose ] && [ \"${2:-}\" = version ]; then echo 'Docker Compose version v2.0.0'; exit 0; fi\n"
        "if [ \"${1:-}\" = --version ]; then echo 'Docker version 27.0.0'; exit 0; fi\n"
        "exit 1\n",
    )


def test_core_capabilities_are_verified_from_a_manifest(tmp_path: Path) -> None:
    bin_dir = _core_path(tmp_path)
    os_release = tmp_path / "os-release"
    os_release.write_text('ID=arch\nID_LIKE=arch\n', encoding="utf-8")
    env = os.environ.copy()
    env.update({"PATH": str(bin_dir), "EXOCORTEX_OS_RELEASE": str(os_release)})

    result = subprocess.run(
        [sys.executable, str(CHECKER), "--manifest", str(MANIFEST), "--profile", "core", "--json"],
        cwd=REPO,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["schema"] == "exocortex-capability-report/v1"
    assert report["platform"]["id"] == "arch"
    assert report["platform"]["package_manager"] == "pacman"
    assert report["summary"]["failed"] == 0
    assert {item["id"] for item in report["capabilities"]} >= {
        "hermes-runtime",
        "python-runtime",
        "git-client",
        "file-sync",
        "posix-shell",
    }


def test_missing_system_capability_reports_native_os_recipe(tmp_path: Path) -> None:
    bin_dir = _core_path(tmp_path, include_git=False)
    os_release = tmp_path / "os-release"
    os_release.write_text("ID=arch\n", encoding="utf-8")
    env = os.environ.copy()
    env.update({"PATH": str(bin_dir), "EXOCORTEX_OS_RELEASE": str(os_release)})

    result = subprocess.run(
        [sys.executable, str(CHECKER), "--manifest", str(MANIFEST), "--profile", "core", "--json"],
        cwd=REPO,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
    )

    assert result.returncode == 1
    report = json.loads(result.stdout)
    git = next(item for item in report["capabilities"] if item["id"] == "git-client")
    assert git["status"] == "fail"
    assert git["remediation"] == "sudo pacman -S --needed git"


def test_full_profile_reports_missing_notebooklm_user_tools(tmp_path: Path) -> None:
    bin_dir = _core_path(tmp_path)
    _add_docker(bin_dir)
    os_release = tmp_path / "os-release"
    os_release.write_text("ID=ubuntu\nID_LIKE=debian\n", encoding="utf-8")
    env = os.environ.copy()
    env.update({"PATH": str(bin_dir), "EXOCORTEX_OS_RELEASE": str(os_release)})

    result = subprocess.run(
        [sys.executable, str(CHECKER), "--manifest", str(MANIFEST), "--profile", "full", "--json"],
        cwd=REPO,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
    )

    assert result.returncode == 1
    report = json.loads(result.stdout)
    notebooklm = next(item for item in report["capabilities"] if item["id"] == "notebooklm-tools")
    assert notebooklm["layer"] == "user-tool"
    assert notebooklm["status"] == "fail"
    assert "uv tool install notebooklm-mcp-cli" in notebooklm["remediation"]
    assert "nlm=ausente" in notebooklm["evidence"]
    assert "notebooklm-mcp=ausente" in notebooklm["evidence"]

    degraded = subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--manifest",
            str(MANIFEST),
            "--profile",
            "full",
            "--allow-degraded-services",
            "--json",
        ],
        cwd=REPO,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert degraded.returncode == 1


def test_capability_fails_when_user_tool_version_is_below_minimum(tmp_path: Path) -> None:
    bin_dir = _core_path(tmp_path)
    _add_docker(bin_dir)
    _write_executable(bin_dir / "nlm", "#!/usr/bin/env bash\necho 'nlm version 0.6.9'\n")
    _write_executable(bin_dir / "notebooklm-mcp", "#!/usr/bin/env bash\nexit 0\n")
    os_release = tmp_path / "os-release"
    os_release.write_text("ID=arch\n", encoding="utf-8")
    env = os.environ.copy()
    env.update({"PATH": str(bin_dir), "EXOCORTEX_OS_RELEASE": str(os_release)})

    result = subprocess.run(
        [sys.executable, str(CHECKER), "--manifest", str(MANIFEST), "--profile", "full", "--json"],
        cwd=REPO,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
    )

    assert result.returncode == 1
    report = json.loads(result.stdout)
    notebooklm = next(item for item in report["capabilities"] if item["id"] == "notebooklm-tools")
    assert notebooklm["status"] == "fail"
    assert "0.6.9 < 0.7.0" in notebooklm["evidence"]


def test_notebooklm_is_a_registration_stage_without_implicit_installers() -> None:
    spec = importlib.util.spec_from_file_location("capability_installer_test", REPO / "scripts" / "exocortex_install.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    core_ids = [stage.id for stage in module.selected_stages("core")]
    full_ids = [stage.id for stage in module.selected_stages("full")]
    step = (REPO / "setup" / "step-09-integration-notebooklm.sh").read_text(encoding="utf-8")

    assert "notebooklm" not in core_ids
    assert "notebooklm" in full_ids
    assert "pip install" not in step
    assert "curl -LsSf" not in step
    assert "_install_nlm" not in step
    assert "hermes mcp test notebooklm" in step


def test_installer_preflight_delegates_to_capability_manifest(tmp_path: Path, monkeypatch) -> None:
    spec = importlib.util.spec_from_file_location("capability_preflight_test", REPO / "scripts" / "exocortex_install.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    bin_dir = _core_path(tmp_path)
    os_release = tmp_path / "os-release"
    os_release.write_text("ID=arch\n", encoding="utf-8")
    monkeypatch.setenv("PATH", str(bin_dir))
    monkeypatch.setenv("EXOCORTEX_OS_RELEASE", str(os_release))

    report = module.preflight("core", require_services=False)

    assert report["ok"] is True
    assert report["platform"]["package_manager"] == "pacman"
    assert any(check["id"] == "capability:git-client" for check in report["checks"])


def test_firecrawl_mcp_is_strict_unless_service_degradation_is_explicit(tmp_path: Path) -> None:
    bin_dir = _core_path(tmp_path)
    _add_docker(bin_dir)
    _write_executable(bin_dir / "nlm", "#!/usr/bin/env bash\necho 'nlm version 0.7.7'\n")
    _write_executable(bin_dir / "notebooklm-mcp", "#!/usr/bin/env bash\nexit 0\n")
    os_release = tmp_path / "os-release"
    os_release.write_text("ID=ubuntu\n", encoding="utf-8")
    env = os.environ.copy()
    env.update({"PATH": str(bin_dir), "EXOCORTEX_OS_RELEASE": str(os_release)})

    base_command = [sys.executable, str(CHECKER), "--manifest", str(MANIFEST), "--profile", "full", "--json"]
    strict = subprocess.run(base_command, cwd=REPO, env=env, text=True, capture_output=True, timeout=60)
    degraded = subprocess.run(
        [*base_command, "--allow-degraded-services"],
        cwd=REPO,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
    )

    assert strict.returncode == 1
    strict_report = json.loads(strict.stdout)
    firecrawl = next(item for item in strict_report["capabilities"] if item["id"] == "firecrawl-mcp")
    assert firecrawl["status"] == "fail"
    assert firecrawl["remediation"] == "npm install --global firecrawl-mcp@3.22.0"
    assert degraded.returncode == 0
    degraded_report = json.loads(degraded.stdout)
    degraded_firecrawl = next(item for item in degraded_report["capabilities"] if item["id"] == "firecrawl-mcp")
    assert degraded_firecrawl["status"] == "warn"


def test_system_package_provenance_is_queried_through_native_manager(tmp_path: Path) -> None:
    bin_dir = _core_path(tmp_path)
    _write_executable(
        bin_dir / "pacman",
        "#!/usr/bin/env bash\n"
        "if [ \"${1:-}\" = -Qo ]; then printf '%s is owned by fixture-package 1.2.3\\n' \"${2:-}\"; exit 0; fi\n"
        "exit 1\n",
    )
    os_release = tmp_path / "os-release"
    os_release.write_text("ID=arch\n", encoding="utf-8")
    env = os.environ.copy()
    env.update({"PATH": str(bin_dir), "EXOCORTEX_OS_RELEASE": str(os_release)})

    result = subprocess.run(
        [sys.executable, str(CHECKER), "--manifest", str(MANIFEST), "--profile", "core", "--json"],
        cwd=REPO,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
    )

    assert result.returncode == 0
    report = json.loads(result.stdout)
    git = next(item for item in report["capabilities"] if item["id"] == "git-client")
    assert git["provenance"]["git"] == "os-package:fixture-package 1.2.3"


def test_deterministic_verifier_rechecks_declared_capabilities() -> None:
    verifier = (REPO / "scripts" / "verify_exocortex_install.py").read_text(encoding="utf-8")

    assert "check_capabilities.py" in verifier
    assert 'record("capabilities"' in verifier


def test_full_verifier_checks_notebooklm_auth_and_firecrawl_mcp() -> None:
    verifier = (REPO / "scripts" / "verify_exocortex_install.py").read_text(encoding="utf-8")

    assert '"nlm", "notebook", "list", "--title"' in verifier
    assert 'for mcp_name in ("notebooklm", "firecrawl")' in verifier
    assert '[hermes, "mcp", "test", mcp_name]' in verifier


def test_firecrawl_stage_registers_stdio_adapter_against_local_backend() -> None:
    step = (REPO / "setup" / "step-11c-integration-firecrawl.sh").read_text(encoding="utf-8")

    assert "--command firecrawl-mcp" in step
    assert 'FIRECRAWL_API_URL=${FIRECRAWL_BASE_URL}' in step
    assert 'hermes mcp test firecrawl' in step


@pytest.mark.parametrize(
    ("os_release", "manager", "recipe"),
    [
        ("ID=ubuntu\nID_LIKE=debian\n", "apt", "sudo apt-get install git"),
        ("ID=fedora\n", "dnf", "sudo dnf install git"),
        ("ID=arch\n", "pacman", "sudo pacman -S --needed git"),
    ],
)
def test_linux_family_selects_native_package_recipe(
    tmp_path: Path,
    os_release: str,
    manager: str,
    recipe: str,
) -> None:
    bin_dir = _core_path(tmp_path, include_git=False)
    release_path = tmp_path / "os-release"
    release_path.write_text(os_release, encoding="utf-8")
    env = os.environ.copy()
    env.update({"PATH": str(bin_dir), "EXOCORTEX_OS_RELEASE": str(release_path)})

    result = subprocess.run(
        [sys.executable, str(CHECKER), "--profile", "core", "--json"],
        cwd=REPO,
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
    )

    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["platform"]["package_manager"] == manager
    git = next(item for item in report["capabilities"] if item["id"] == "git-client")
    assert git["remediation"] == recipe


def test_capability_manifest_has_unique_ids_and_supported_layers() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    capabilities = manifest["capabilities"]
    ids = [item["id"] for item in capabilities]

    assert manifest["schema"] == "exocortex-capabilities/v1"
    assert len(ids) == len(set(ids))
    assert all(set(item["profiles"]) <= {"core", "full"} for item in capabilities)
    assert all(item["layer"] in {"runtime", "system", "service", "user-tool"} for item in capabilities)
    assert all(item["commands"] for item in capabilities)


def test_checker_rejects_an_invalid_manifest_schema(tmp_path: Path) -> None:
    manifest = tmp_path / "invalid-capabilities.json"
    manifest.write_text('{"schema":"wrong/v0","platforms":{},"capabilities":[]}', encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(CHECKER), "--manifest", str(manifest), "--profile", "core", "--json"],
        cwd=REPO,
        text=True,
        capture_output=True,
        timeout=60,
    )

    assert result.returncode == 2
    assert "schema" in result.stderr.lower()


def test_transient_external_probe_is_retried(monkeypatch) -> None:
    spec = importlib.util.spec_from_file_location("capability_verifier_retry", REPO / "scripts" / "verify_exocortex_install.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    responses = iter([(1, "transient"), (0, "ok")])
    monkeypatch.setattr(module, "run", lambda *args, **kwargs: next(responses))

    code, output, attempts = module.run_with_retry(["nlm", "notebook", "list", "--title"], attempts=3, delay=0)

    assert code == 0
    assert output == "ok"
    assert attempts == 2
