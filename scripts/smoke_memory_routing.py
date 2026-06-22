#!/usr/bin/env python3
"""Smoke test for Exocortex/Hermes memory routing provision.

Checks only local deterministic state. Optional chat smoke is enabled with
--chat-smoke because it may call an external LLM provider.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None

REQUIRED_HINDSIGHT = {
    "memory_mode": "tools",
    "auto_recall": False,
    "auto_retain": True,
    "recall_budget": "low",
    "recall_max_input_chars": 800,
}

PROTOCOL_PHRASES = [
    "Chame `hindsight_recall` antes de responder",
    "Acervo confirma",
    "memória rápida só inicializa",
]


def run(cmd: list[str], *, timeout: int = 120, env: dict[str, str] | None = None) -> dict[str, Any]:
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False, env=env)
    return {"cmd": cmd, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def check_hindsight(hermes_home: Path) -> dict[str, Any]:
    path = hermes_home / "hindsight" / "config.json"
    if not path.exists():
        return {"ok": False, "path": str(path), "error": "missing config"}
    cfg = json.loads(path.read_text(encoding="utf-8"))
    mismatches = {k: {"expected": v, "actual": cfg.get(k)} for k, v in REQUIRED_HINDSIGHT.items() if cfg.get(k) != v}
    return {"ok": not mismatches, "path": str(path), "mismatches": mismatches}


def check_hermes_config(hermes_home: Path) -> dict[str, Any]:
    path = hermes_home / "config.yaml"
    if yaml is None:
        return {"ok": False, "path": str(path), "error": "PyYAML unavailable"}
    cfg = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}
    memory = (cfg or {}).get("memory") or {}
    checks = {
        "provider": memory.get("provider") == "hindsight",
        "memory_enabled": memory.get("memory_enabled") is True,
        "user_profile_enabled": memory.get("user_profile_enabled") is True,
    }
    return {"ok": all(checks.values()), "path": str(path), "checks": checks}


def check_soul(hermes_home: Path) -> dict[str, Any]:
    path = hermes_home / "SOUL.md"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    checks = {phrase: phrase in text for phrase in PROTOCOL_PHRASES}
    return {"ok": all(checks.values()), "path": str(path), "checks": checks}


def check_memory_budget(hermes_home: Path, limit: int = 2200) -> dict[str, Any]:
    path = hermes_home / "memories" / "MEMORY.md"
    chars = len(path.read_text(encoding="utf-8")) if path.exists() else 0
    return {"ok": chars <= limit // 2, "path": str(path), "chars": chars, "limit": limit}


def check_acervo_index(acervo: Path, microverso: str | None, *, global_scope: bool = False) -> dict[str, Any]:
    script = acervo / "global" / "tools" / "acervo_hindsight_index.py"
    if not script.exists():
        return {"ok": False, "path": str(script), "error": "missing script"}
    env = os.environ.copy()
    env["ACERVO"] = str(acervo)
    pyc = run([sys.executable, "-m", "py_compile", str(script)], env=env)
    scan_cmd = [sys.executable, str(script), "scan"]
    if global_scope:
        scan_cmd += ["--global"]
    elif microverso:
        scan_cmd += ["--microverso", microverso]
    else:
        scan_cmd += ["--all"]
    scan = run(scan_cmd, env=env)
    report = run([sys.executable, str(script), "report"], env=env)
    scan_errors = None
    try:
        scan_errors = json.loads(scan["stdout"]).get("errors")
    except Exception:
        pass
    ok = pyc["returncode"] == 0 and scan["returncode"] == 0 and report["returncode"] == 0 and scan_errors == 0
    return {"ok": ok, "path": str(script), "py_compile": pyc, "scan": scan, "report": report}


def check_chat_smoke() -> dict[str, Any]:
    query = "O que decidimos sobre o modelo operacional de memória do Exocórtex? Responda em até 5 linhas e cite a origem."
    cmd = [
        "hermes", "chat", "-q", query,
        "--provider", "openai-codex", "-m", "gpt-5.4", "-v",
        "--toolsets", "memory,file,skills,session_search,terminal",
    ]
    result = run(cmd, timeout=240)
    text = result["stdout"] + result["stderr"]
    result["ok"] = result["returncode"] == 0 and "hindsight_recall" in text and ("adr-019" in text.lower() or "Acervo" in text)
    return result


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Smoke test memory routing")
    p.add_argument("--hermes-home", default=os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))
    p.add_argument("--acervo", default=os.environ.get("ACERVO") or os.environ.get("EXOCORTEX_HOME", str(Path.home() / "exocortex")) + "/acervo")
    p.add_argument("--microverso", default="exocortex-ops")
    p.add_argument("--scan-global", action="store_true", help="scan global Acervo layer before the selected microverso")
    p.add_argument("--skip-micro-scan", action="store_true", help="only scan global layer when paired with --scan-global")
    p.add_argument("--scan-all", action="store_true", help="scan all Acervo scopes instead of targeted canonical scopes")
    p.add_argument("--chat-smoke", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    hermes_home = Path(args.hermes_home).expanduser().resolve()
    acervo = Path(args.acervo).expanduser().resolve()
    report: dict[str, Any] = {
        "hindsight": check_hindsight(hermes_home),
        "hermes_config": check_hermes_config(hermes_home),
        "soul": check_soul(hermes_home),
        "memory_budget": check_memory_budget(hermes_home),
    }
    if args.scan_all:
        report["acervo_index"] = check_acervo_index(acervo, None)
    else:
        if args.scan_global:
            report["acervo_index_global"] = check_acervo_index(acervo, None, global_scope=True)
        if not args.skip_micro_scan:
            report["acervo_index_micro"] = check_acervo_index(acervo, args.microverso)
    if args.chat_smoke:
        report["chat_smoke"] = check_chat_smoke()
    ok = all(item.get("ok") for item in report.values())
    print(json.dumps({"ok": ok, "checks": report}, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
