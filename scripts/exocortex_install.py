#!/usr/bin/env python3
"""Idempotent plan/apply/verify installer for Exocórtex over an existing Hermes.

The installer deliberately does not install Hermes or system packages. It manages
only Exocórtex-owned artifacts, provisions selected local services, and runs a
small behavioral acceptance suite instead of the historical full dogfood catalog.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).expanduser()
DEFAULT_EXOCORTEX_HOME = Path(os.environ.get("EXOCORTEX_HOME", Path.home() / "exocortex")).expanduser()


@dataclass(frozen=True)
class Stage:
    id: str
    title: str
    command: tuple[str, ...]
    profiles: frozenset[str] = frozenset({"core", "full"})
    critical: bool = True
    service: str | None = None
    env: dict[str, str] = field(default_factory=dict)


STAGES: tuple[Stage, ...] = (
    Stage("structure", "Criar estrutura gerenciada", ("bash", "setup/step-02-create-structure.sh")),
    Stage("skills", "Instalar skills do Exocórtex", ("bash", "setup/step-03-install-skills.sh")),
    Stage("acervo", "Semear o Acervo sem sobrescrever conteúdo vivo", ("bash", "setup/step-04-install-acervo.sh")),
    Stage("identity", "Instalar ou reconciliar a identidade Exocórtex", ("bash", "setup/step-07-install-identity.sh")),
    Stage("profiles", "Instalar profiles e bundle", ("bash", "setup/step-05-install-profiles.sh")),
    Stage(
        "compile-soul",
        "Compilar regras comportamentais no SOUL.md",
        (
            "python3",
            "scripts/compile_soul.py",
            "--skills-dir",
            "{HERMES_HOME}/skills/excrtx",
            "--soul",
            "{HERMES_HOME}/SOUL.md",
        ),
    ),
    Stage(
        "memory-routing",
        "Provisionar roteamento Acervo + memória operacional",
        (
            "python3",
            "scripts/provision_memory_routing.py",
            "--hermes-home",
            "{HERMES_HOME}",
            "--acervo",
            "{ACERVO}",
            "--repo-root",
            "{REPO_ROOT}",
            "--profile",
            "{PROFILE}",
            "--scan-global",
            "--skip-micro-scan",
            "--consolidate-memory",
        ),
    ),
    Stage("acervo-mcp", "Registrar o control plane semântico do Acervo", ("bash", "setup/step-11b-integration-acervo-mcp.sh")),
    Stage(
        "notebooklm",
        "Registrar e verificar NotebookLM CLI + MCP",
        ("bash", "setup/step-09-integration-notebooklm.sh"),
        profiles=frozenset({"full"}),
    ),
    Stage(
        "hindsight",
        "Provisionar Hindsight self-hosted",
        ("bash", "setup/step-01-hindsight.sh"),
        profiles=frozenset({"full"}),
        service="hindsight",
        env={"EXOCORTEX_ENABLE_HINDSIGHT": "1"},
        critical=False,
    ),
    Stage(
        "firecrawl",
        "Provisionar Firecrawl self-hosted",
        ("bash", "setup/step-11c-integration-firecrawl.sh"),
        profiles=frozenset({"full"}),
        service="firecrawl",
        env={"EXOCORTEX_ENABLE_FIRECRAWL": "1"},
        critical=False,
    ),
    Stage(
        "webui",
        "Provisionar Hermes WebUI",
        ("bash", "setup/step-10b-hermes-webui.sh"),
        profiles=frozenset({"full"}),
        service="webui",
        env={"EXOCORTEX_ENABLE_HERMES_WEBUI": "1"},
        critical=False,
    ),
    Stage(
        "webui-acervo",
        "Registrar Acervo Cognitivo na WebUI",
        ("bash", "setup/step-10c-provision-acervo-workspace.sh"),
        profiles=frozenset({"full"}),
        service="webui",
        env={"EXOCORTEX_ENABLE_HERMES_WEBUI": "1"},
        critical=False,
    ),
    Stage(
        "verify",
        "Verificar contrato instalado",
        (
            "python3",
            "scripts/verify_exocortex_install.py",
            "--profile",
            "{PROFILE}",
            "--json-report",
            "{REPORT_DIR}/verification.json",
        ),
    ),
)

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def selected_stages(profile: str) -> list[Stage]:
    return [stage for stage in STAGES if profile in stage.profiles]


def preflight(profile: str, require_services: bool) -> dict[str, object]:
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "check_capabilities.py"),
        "--profile",
        profile,
        "--json",
    ]
    if not require_services:
        command.append("--allow-degraded-services")
    completed = subprocess.run(command, text=True, capture_output=True, timeout=60, check=False)
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {
            "ok": False,
            "services_available": False,
            "platform": {"id": "unknown", "package_manager": "unknown"},
            "checks": [{"id": "capability-manifest", "status": "fail", "evidence": completed.stderr.strip()}],
        }

    checks = [
        {
            "id": f"capability:{item['id']}",
            "status": item["status"],
            "evidence": item["evidence"],
            "remediation": item["remediation"],
            "layer": item["layer"],
        }
        for item in report["capabilities"]
    ]
    service_checks = [item for item in report["capabilities"] if item["layer"] == "service"]
    services_available = all(item["status"] == "pass" for item in service_checks)
    return {
        "ok": report["summary"]["failed"] == 0,
        "services_available": services_available,
        "platform": report["platform"],
        "checks": checks,
    }


def managed_snapshot(hermes_home: Path, report_dir: Path) -> Path | None:
    candidates = (
        hermes_home / "SOUL.md",
        hermes_home / "skills" / "excrtx",
        hermes_home / "profiles" / "manut",
        hermes_home / "profiles" / "chat",
        hermes_home / "skill-bundles" / "exocortex-alpha.yaml",
    )
    existing = [path for path in candidates if path.exists()]
    if not existing:
        return None
    snapshot = report_dir / "pre-install-managed-files.tar.gz"

    def distributable_only(member: tarfile.TarInfo) -> tarfile.TarInfo | None:
        excluded = {".runtime", ".venv", "node_modules", "__pycache__"}
        return None if excluded.intersection(Path(member.name).parts) or member.name.endswith(".pyc") else member

    with tarfile.open(snapshot, "w:gz") as archive:
        for path in existing:
            archive.add(path, arcname=path.relative_to(hermes_home), filter=distributable_only)
    return snapshot


def secret_values(env: dict[str, str]) -> list[str]:
    names = re.compile(r"(KEY|TOKEN|PASSWORD|SECRET)$")
    return sorted(
        {value for name, value in env.items() if value and len(value) >= 8 and names.search(name)},
        key=len,
        reverse=True,
    )


def sanitize(text: str, secrets: Iterable[str]) -> str:
    for secret in secrets:
        text = text.replace(secret, "<redacted>")
    return text


def render_command(stage: Stage, values: dict[str, str]) -> list[str]:
    return [part.format_map(values) for part in stage.command]


def run_stage(
    stage: Stage,
    *,
    env: dict[str, str],
    values: dict[str, str],
    log_dir: Path,
    review_each: bool,
    assume_yes: bool,
    services_available: bool,
    require_services: bool,
) -> dict[str, object]:
    if stage.service and not services_available:
        status = "fail" if require_services else "skip"
        return {
            "id": stage.id,
            "title": stage.title,
            "status": status,
            "critical": require_services,
            "reason": "capacidades exigidas pelos serviços indisponíveis",
            "duration_seconds": 0.0,
        }

    if review_each and not assume_yes:
        answer = input(f"Executar '{stage.title}'? [S/n] ").strip().lower()
        if answer not in ("", "s", "sim", "y", "yes"):
            return {
                "id": stage.id,
                "title": stage.title,
                "status": "skip",
                "critical": stage.critical,
                "reason": "pulada pelo operador",
                "duration_seconds": 0.0,
            }

    command = render_command(stage, values)
    stage_env = dict(env)
    stage_env.update(stage.env)
    log_path = log_dir / f"{stage.id}.log"
    started = time.monotonic()
    print(f"→ {stage.title}")
    try:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=stage_env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=1800 if stage.service else 600,
            check=False,
        )
        raw_output = result.stdout or ""
        exit_code = result.returncode
    except subprocess.TimeoutExpired as exc:
        timeout_output = exc.stdout or ""
        if isinstance(timeout_output, bytes):
            timeout_output = timeout_output.decode("utf-8", errors="replace")
        raw_output = timeout_output + "\nTIMEOUT"
        exit_code = 124
    cleaned = sanitize(raw_output, secret_values(stage_env))
    log_path.write_text(cleaned, encoding="utf-8")
    duration = round(time.monotonic() - started, 3)
    if cleaned.strip():
        tail = cleaned.strip().splitlines()[-8:]
        for line in tail:
            print(f"  {line}")
    status = "pass" if exit_code == 0 else ("warn" if stage.service and not require_services else "fail")
    symbol = "✓" if status == "pass" else "⚠" if status == "warn" else "✗"
    print(f"  {symbol} {stage.id}: {status} ({duration:.1f}s)")
    return {
        "id": stage.id,
        "title": stage.title,
        "status": status,
        "critical": stage.critical or (bool(stage.service) and require_services),
        "exit_code": exit_code,
        "duration_seconds": duration,
        "log": str(log_path),
    }


def run_acceptance(
    *,
    hermes_home: Path,
    report_dir: Path,
    env: dict[str, str],
    model: str | None,
) -> dict[str, object]:
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "verify_exocortex_behavior.py"),
        "--json-report",
        str(report_dir / "behavior-acceptance.json"),
    ]
    if model:
        command.extend(("--model", model))
    started = time.monotonic()
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        env={**env, "HERMES_HOME": str(hermes_home)},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=900,
        check=False,
    )
    output = sanitize(result.stdout or "", secret_values(env))
    log = report_dir / "behavior-acceptance.log"
    log.write_text(output, encoding="utf-8")
    print(output.rstrip())
    return {
        "id": "behavior-acceptance",
        "title": "Dogfood mínimo do contrato cognitivo",
        "status": "pass" if result.returncode == 0 else "fail",
        "critical": True,
        "exit_code": result.returncode,
        "duration_seconds": round(time.monotonic() - started, 3),
        "log": str(log),
    }


def print_plan(profile: str, acceptance: str, require_services: bool) -> None:
    print(f"Perfil: {profile}")
    print("Contrato: Hermes já instalado e configurado; nenhum pacote de sistema será instalado.")
    for number, stage in enumerate(selected_stages(profile), start=1):
        marker = "obrigatório" if stage.critical or (stage.service and require_services) else "degradável"
        print(f"  {number:02d}. {stage.id:<18} {stage.title} [{marker}]")
    print(f"  {'--':>2}. behavior-acceptance Dogfood mínimo do contrato cognitivo [{acceptance}]")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Instalador v2 do Exocórtex sobre Hermes existente")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("plan", "apply", "verify"):
        p = sub.add_parser(command)
        p.add_argument("--profile", choices=("core", "full"), default="full")
        p.add_argument("--hermes-home", type=Path, default=DEFAULT_HERMES_HOME)
        p.add_argument("--exocortex-home", type=Path, default=DEFAULT_EXOCORTEX_HOME)
        p.add_argument(
            "--allow-degraded-services",
            action="store_true",
            help="No perfil full, registra serviços indisponíveis como skip em vez de falhar",
        )
        if command == "apply":
            p.add_argument("--yes", "-y", action="store_true")
            p.add_argument("--review-each", action="store_true")
            p.add_argument("--acceptance", choices=("contract", "skip"), default="contract")
            p.add_argument("--model")
        elif command == "verify":
            p.add_argument("--json-report", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    hermes_home = args.hermes_home.expanduser().resolve()
    exocortex_home = args.exocortex_home.expanduser().resolve()
    acervo_value = os.environ.get("ACERVO")
    acervo = (Path(acervo_value) if acervo_value else exocortex_home / "acervo").expanduser().resolve()

    acceptance = getattr(args, "acceptance", "contract")
    require_services = args.profile == "full" and not args.allow_degraded_services
    if args.command == "plan":
        print_plan(args.profile, acceptance, require_services)
        pre = preflight(args.profile, require_services)
        print(json.dumps(pre, indent=2, ensure_ascii=False))
        return 0 if pre["ok"] else 1

    if args.command == "verify":
        command = [
            sys.executable,
            str(REPO_ROOT / "scripts" / "verify_exocortex_install.py"),
            "--profile",
            args.profile,
        ]
        if args.allow_degraded_services:
            command.append("--allow-degraded-services")
        if args.json_report:
            command.extend(("--json-report", str(args.json_report)))
        env = os.environ.copy()
        env.update({"HERMES_HOME": str(hermes_home), "EXOCORTEX_HOME": str(exocortex_home), "ACERVO": str(acervo)})
        return subprocess.run(command, cwd=REPO_ROOT, env=env, check=False).returncode

    started_at = now_iso()
    print_plan(args.profile, acceptance, require_services)
    pre = preflight(args.profile, require_services)
    if not pre["ok"]:
        print("Preflight falhou. O instalador não altera o sistema para corrigir dependências.", file=sys.stderr)
        print(json.dumps(pre, indent=2, ensure_ascii=False), file=sys.stderr)
        return 2

    if not args.yes:
        answer = input("Aplicar este plano? [s/N] ").strip().lower()
        if answer not in ("s", "sim", "y", "yes"):
            print("Instalação cancelada sem alterações.")
            return 130

    install_root = hermes_home / "exocortex-install"
    install_root.mkdir(parents=True, exist_ok=True)
    lock_path = install_root / "install.lock"
    with lock_path.open("w", encoding="utf-8") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print(f"Outra instalação está em andamento: {lock_path}", file=sys.stderr)
            return 3

        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        report_dir = install_root / "runs" / run_id
        log_dir = report_dir / "logs"
        log_dir.mkdir(parents=True)
        snapshot = managed_snapshot(hermes_home, report_dir)

        env = os.environ.copy()
        env.update(
            {
                "HERMES_HOME": str(hermes_home),
                "EXOCORTEX_HOME": str(exocortex_home),
                "ACERVO": str(acervo),
                "_EXOCORTEX_SCRIPT_DIR": str(REPO_ROOT),
                "INTERACTIVE_MODE": "0",
                "EXOCORTEX_NO_PING": "1",
                "EXOCORTEX_INSTALL_PROFILE": args.profile,
            }
        )
        values = {
            "HERMES_HOME": str(hermes_home),
            "EXOCORTEX_HOME": str(exocortex_home),
            "ACERVO": str(acervo),
            "REPO_ROOT": str(REPO_ROOT),
            "PROFILE": args.profile,
            "REPORT_DIR": str(report_dir),
        }

        results: list[dict[str, object]] = []
        for stage in selected_stages(args.profile):
            result = run_stage(
                stage,
                env=env,
                values=values,
                log_dir=log_dir,
                review_each=args.review_each,
                assume_yes=args.yes,
                services_available=bool(pre["services_available"]),
                require_services=require_services,
            )
            results.append(result)
            if result["status"] == "fail" and result["critical"]:
                break

        critical_failed = any(item["status"] == "fail" and item["critical"] for item in results)
        if not critical_failed and acceptance == "contract":
            results.append(run_acceptance(hermes_home=hermes_home, report_dir=report_dir, env=env, model=args.model))
            critical_failed = results[-1]["status"] == "fail"

        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True, capture_output=True, check=False
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain"], cwd=REPO_ROOT, text=True, capture_output=True, check=False
            ).stdout.strip()
        )
        state = {
            "schema": "exocortex-install/v2",
            "run_id": run_id,
            "started_at": started_at,
            "finished_at": now_iso(),
            "profile": args.profile,
            "source_commit": commit or None,
            "source_dirty": dirty,
            "paths": {
                "hermes_home": str(hermes_home),
                "exocortex_home": str(exocortex_home),
                "acervo": str(acervo),
                "repo_root": str(REPO_ROOT),
            },
            "preflight": pre,
            "snapshot": str(snapshot) if snapshot else None,
            "results": results,
            "status": "fail" if critical_failed else "pass",
        }
        state_path = report_dir / "install-state.json"
        state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        latest = install_root / "latest.json"
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=install_root, delete=False) as tmp:
            json.dump(state, tmp, indent=2, ensure_ascii=False)
            tmp.write("\n")
            temp_path = Path(tmp.name)
        temp_path.replace(latest)

        print(f"Relatório: {state_path}")
        print(f"Estado: {'FALHA' if critical_failed else 'OK'}")
        return 1 if critical_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
