#!/usr/bin/env python3
"""Deterministic verification for an Exocórtex installation.

Unlike the historical dogfood suite, this script checks only the installation
contract: identity, core skills, Acervo, memory routing, MCP wiring, profiles, and
health of services requested by the selected profile.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parent.parent
ESSENTIAL_SKILLS = (
    "excrtx-behavior-vetor",
    "excrtx-behavior-canvas",
    "excrtx-govern-draftfirst",
    "excrtx-behavior-accuracy",
    "excrtx-memory-manager",
    "excrtx-memory-intake",
    "excrtx-quality-antislop",
    "excrtx-quality-gate",
    "excrtx-assess-selftest",
    "excrtx-onboard-welcome",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verificação determinística do Exocórtex instalado")
    parser.add_argument("--profile", choices=("core", "full"), default="full")
    parser.add_argument("--allow-degraded-services", action="store_true")
    parser.add_argument("--json-report", type=Path)
    return parser.parse_args()


def run(command: list[str], *, env: dict[str, str], timeout: int = 120) -> tuple[int, str]:
    started = time.monotonic()
    try:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            check=False,
        )
        output = result.stdout or ""
        code = result.returncode
    except subprocess.TimeoutExpired:
        output = f"timeout após {timeout}s"
        code = 124
    except OSError as exc:
        output = str(exc)
        code = 127
    return code, f"{output.strip()}\n[duração={time.monotonic() - started:.2f}s]"


def run_with_retry(
    command: list[str],
    *,
    env: dict[str, str] | None = None,
    timeout: int = 180,
    attempts: int = 3,
    delay: float = 2,
) -> tuple[int, str, int]:
    effective_env = env or os.environ.copy()
    code = 127
    output = "probe não executado"
    for attempt in range(1, attempts + 1):
        code, output = run(command, env=effective_env, timeout=timeout)
        if code == 0:
            return code, output, attempt
        if attempt < attempts and delay:
            time.sleep(delay)
    return code, output, attempts


def main() -> int:
    args = parse_args()
    hermes_home = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).expanduser().resolve()
    exocortex_home = Path(os.environ.get("EXOCORTEX_HOME", Path.home() / "exocortex")).expanduser().resolve()
    acervo = Path(os.environ.get("ACERVO", exocortex_home / "acervo")).expanduser().resolve()
    env = os.environ.copy()
    env.update({"HERMES_HOME": str(hermes_home), "EXOCORTEX_HOME": str(exocortex_home), "ACERVO": str(acervo)})

    checks: list[dict[str, object]] = []

    def record(check_id: str, title: str, passed: bool, evidence: str, *, degraded: bool = False) -> None:
        status = "pass" if passed else ("warn" if degraded else "fail")
        checks.append({"id": check_id, "title": title, "status": status, "evidence": evidence})
        print(f"  {'✓' if status == 'pass' else '⚠' if status == 'warn' else '✗'} {check_id}: {status} — {evidence}")

    print("Verificação determinística do contrato instalado")

    capability_command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "check_capabilities.py"),
        "--profile",
        args.profile,
        "--json",
    ]
    if args.allow_degraded_services:
        capability_command.append("--allow-degraded-services")
    code, output = run(capability_command, env=env, timeout=60)
    record("capabilities", "Capacidades declaradas para o SO", code == 0, f"exit={code}; {output.splitlines()[-1] if output else ''}")

    hermes = shutil.which("hermes")
    record("hermes-cli", "Hermes presente", bool(hermes), hermes or "ausente")
    if hermes:
        code, output = run([hermes, "config", "check"], env=env, timeout=30)
        record("hermes-config", "Configuração Hermes válida", code == 0, f"exit={code}; {output.splitlines()[-1] if output else ''}")

    soul = hermes_home / "SOUL.md"
    soul_text = soul.read_text(encoding="utf-8") if soul.is_file() else ""
    identity_ok = "Exocórtex.IA" in soul_text and "Hermes Agent" in soul_text
    record("identity", "Identidade Exocórtex sobre Hermes", identity_ok, str(soul))
    compiled_ok = "COMPILED_RULES_START" in soul_text and "Draft-First" in soul_text
    record("compiled-rules", "Regras comportamentais compiladas", compiled_ok, "markers compiled_rules + Draft-First")

    missing_skills = [name for name in ESSENTIAL_SKILLS if not (hermes_home / "skills" / "excrtx" / name / "SKILL.md").is_file()]
    record(
        "skills-core",
        "Skills essenciais",
        not missing_skills,
        "10/10" if not missing_skills else "faltam: " + ", ".join(missing_skills),
    )

    layers = ("macro", "global", "micro", "shared")
    missing_layers = [layer for layer in layers if not (acervo / layer).is_dir()]
    record("acervo-layout", "Camadas do Acervo", not missing_layers, "4/4" if not missing_layers else "faltam: " + ", ".join(missing_layers))
    macro_soul = acervo / "macro" / "SOUL.md"
    record(
        "macroverso",
        "Macroverso disponível antes ou depois do onboarding",
        macro_soul.is_file(),
        str(macro_soul),
    )

    profile_files = (hermes_home / "profiles" / "manut" / "profile.yaml", hermes_home / "profiles" / "chat" / "profile.yaml")
    missing_profiles = [str(path) for path in profile_files if not path.is_file()]
    record("profiles", "Profiles operacionais", not missing_profiles, "manut + chat" if not missing_profiles else "faltam: " + ", ".join(missing_profiles))

    bundle = hermes_home / "skill-bundles" / "exocortex-alpha.yaml"
    record("bundle", "Bundle Exocórtex", bundle.is_file(), str(bundle))

    index_script = acervo / "global" / "tools" / "acervo_hindsight_index.py"
    index_state = acervo / "global" / "tools" / "state" / "acervo_hindsight_index.json"
    routing_ok = (
        "## Protocolo de Memória e Contexto" in soul_text
        and index_script.is_file()
        and index_state.is_file()
    )
    routing_evidence = "protocolo no SOUL + script/state AcervoIndex"
    if args.profile == "full":
        hindsight_config = hermes_home / "hindsight" / "config.json"
        hermes_config_text = (hermes_home / "config.yaml").read_text(encoding="utf-8") if (hermes_home / "config.yaml").is_file() else ""
        try:
            hindsight_data = json.loads(hindsight_config.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            hindsight_data = {}
        routing_ok = routing_ok and hindsight_data.get("memory_mode") == "tools" and "provider: hindsight" in hermes_config_text
        routing_evidence += " + provider Hindsight"
    record("memory-routing", "Roteamento de memória", routing_ok, routing_evidence)

    mcp_server = REPO_ROOT / "scripts" / "acervo_mcp_server.py"
    code, output = run([sys.executable, str(mcp_server), "--self-test", "--acervo-root", str(acervo)], env=env, timeout=120)
    record("acervo-mcp-selftest", "Acervo MCP local", code == 0, f"exit={code}; {output.splitlines()[-1] if output else ''}")
    if hermes:
        code, output = run([hermes, "mcp", "test", "acervo"], env=env, timeout=120)
        record("acervo-mcp-runtime", "Acervo MCP no Hermes", code == 0, f"exit={code}; {output.splitlines()[-1] if output else ''}")

    if args.profile == "full":
        code, output, attempts = run_with_retry(
            ["nlm", "notebook", "list", "--title"],
            env=env,
            timeout=120,
        )
        record(
            "notebooklm-auth",
            "NotebookLM com autenticação funcional",
            code == 0,
            f"exit={code}; tentativas={attempts}; {output.splitlines()[-1] if output else ''}",
        )
        if hermes:
            for mcp_name in ("notebooklm", "firecrawl"):
                code, output = run([hermes, "mcp", "test", mcp_name], env=env, timeout=120)
                record(
                    f"mcp:{mcp_name}",
                    f"MCP {mcp_name} conectado",
                    code == 0,
                    f"exit={code}; {output.splitlines()[-1] if output else ''}",
                    degraded=args.allow_degraded_services and mcp_name == "firecrawl",
                )

        service_smokes = {
            "hindsight": REPO_ROOT / "provision" / "hindsight" / "scripts" / "smoke.sh",
            "firecrawl": REPO_ROOT / "provision" / "firecrawl" / "scripts" / "smoke.sh",
            "webui": REPO_ROOT / "provision" / "hermes-webui" / "scripts" / "smoke.sh",
        }
        for name, script in service_smokes.items():
            code, output = run(["bash", str(script)], env=env, timeout=180)
            tail = output.splitlines()[-1] if output else "sem saída"
            record(
                f"service:{name}",
                f"Serviço self-hosted {name}",
                code == 0,
                f"exit={code}; {tail}",
                degraded=args.allow_degraded_services,
            )

    summary = {
        "total": len(checks),
        "passed": sum(item["status"] == "pass" for item in checks),
        "warnings": sum(item["status"] == "warn" for item in checks),
        "failed": sum(item["status"] == "fail" for item in checks),
    }
    report = {
        "schema": "exocortex-install-verification/v2",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "profile": args.profile,
        "paths": {"hermes_home": str(hermes_home), "exocortex_home": str(exocortex_home), "acervo": str(acervo)},
        "summary": summary,
        "checks": checks,
    }
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Relatório determinístico: {args.json_report}")

    print(f"Verificação: {summary['passed']} pass, {summary['warnings']} warn, {summary['failed']} fail")
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
