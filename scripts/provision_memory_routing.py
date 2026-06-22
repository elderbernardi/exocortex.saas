#!/usr/bin/env python3
"""Provision the Exocortex/Hermes memory routing model.

Idempotent local provisioner for:
- Hindsight tools-first config
- Hermes memory provider flags
- SOUL memory/context protocol block
- MEMORY.md fast-layer budget guard
- AcervoIndex script/state presence
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None

PROTOCOL_TITLE = "## Protocolo de Memória e Contexto"
PROTOCOL_BLOCK = """## Protocolo de Memória e Contexto

Quando a resposta depender de passado, decisão, estado de projeto, contexto multi-sessão ou conhecimento fora do turno atual:

1. Chame `hindsight_recall` antes de responder.
2. Se o resultado apontar para conhecimento ou decisão canônica, leia o arquivo exato no Acervo antes da resposta final.
3. Use `session_search` apenas quando a necessidade for literalidade de conversa, auditoria textual ou reconstrução de transcript.
4. Use `MEMORY.md` e `USER.md` só para invariantes, preferências duráveis e quirks que precisem estar no prompt antes da primeira ferramenta.
5. Em conflito, vale: SOUL > contratos > Acervo > session_search > Hindsight > memória rápida.

Regra curta:
- Hindsight recupera.
- Acervo confirma.
- session_search prova.
- memória rápida só inicializa.
"""

DESIRED_HINDSIGHT = {
    "mode": "local_external",
    "api_url": "http://localhost:8888",
    "bank_id": "exocortex",
    "memory_mode": "tools",
    "auto_recall": False,
    "auto_retain": True,
    "retain_async": True,
    "retain_every_n_turns": 2,
    "recall_budget": "low",
    "recall_prefetch_method": "recall",
    "recall_types": "observation",
    "recall_max_tokens": 1200,
    "recall_max_input_chars": 800,
}

BOOTSTRAP_MEMORY = """Terminal Hermes sanitiza segredos `sk-*`; para gravar chaves ou inspecionar env do gateway, usar `execute_code` Python ou `/proc/<pid>/environ`.
§
DocBrain (`ProjetoBB/docBrainBB.git`) é privado; nunca citar em README, preflight ou help text. Decisão canônica: `acervo/micro/exocortex-dev/decisions/docbrain-not-public.md`.
§
`last30days`: skill em `skills/last30days/`, symlink em `~/.hermes/skills/research/last30days`, Python `/usr/sbin/python3.14`. Reasoning/visão vêm dos papéis LLM (`EXOCORTEX_DEFAULT_*` / `EXOCORTEX_VISION_*`); chaves de scraping são próprias da skill.
§
Google Workspace OAuth usa project `734420556052` e token `~/.hermes/google_token.json`.
"""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ensure_hindsight_config(hermes_home: Path) -> dict[str, Any]:
    path = hermes_home / "hindsight" / "config.json"
    cfg = load_json(path)
    changed = False
    for key, value in DESIRED_HINDSIGHT.items():
        if cfg.get(key) != value:
            cfg[key] = value
            changed = True
    if changed or not path.exists():
        write_json(path, cfg)
    return {"path": str(path), "changed": changed, "config": cfg}


def ensure_hermes_memory_flags(hermes_home: Path) -> dict[str, Any]:
    path = hermes_home / "config.yaml"
    if yaml is None:
        return {"path": str(path), "changed": False, "warning": "PyYAML unavailable"}
    cfg: dict[str, Any] = {}
    if path.exists():
        cfg = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    memory = cfg.get("memory")
    if not isinstance(memory, dict):
        memory = {}
    before = dict(memory)
    memory.update({
        "provider": "hindsight",
        "memory_enabled": True,
        "user_profile_enabled": True,
    })
    cfg["memory"] = memory
    changed = before != memory or not path.exists()
    if changed:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(cfg, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return {"path": str(path), "changed": changed}


def patch_soul(hermes_home: Path) -> dict[str, Any]:
    path = hermes_home / "SOUL.md"
    if not path.exists():
        return {"path": str(path), "changed": False, "warning": "SOUL.md missing"}
    text = path.read_text(encoding="utf-8")
    if "<!-- COMPILED_RULES_START -->" in text:
        before_compiled, compiled = text.split("<!-- COMPILED_RULES_START -->", 1)
        compiled = "<!-- COMPILED_RULES_START -->" + compiled
    else:
        before_compiled, compiled = text, ""
    if PROTOCOL_TITLE in before_compiled:
        start = before_compiled.index(PROTOCOL_TITLE)
        next_header = before_compiled.find("\n# ", start + 1)
        if next_header == -1:
            before_compiled = before_compiled[:start].rstrip() + "\n\n" + PROTOCOL_BLOCK.rstrip() + "\n"
        else:
            before_compiled = before_compiled[:start].rstrip() + "\n\n" + PROTOCOL_BLOCK.rstrip() + "\n\n" + before_compiled[next_header + 1 :].lstrip()
    else:
        marker = "## Self-Awareness"
        workspace = "# Workspace Paths"
        if workspace in before_compiled:
            idx = before_compiled.index(workspace)
            before_compiled = before_compiled[:idx].rstrip() + "\n\n" + PROTOCOL_BLOCK.rstrip() + "\n\n" + before_compiled[idx:].lstrip()
        elif marker in before_compiled:
            before_compiled = before_compiled.rstrip() + "\n\n" + PROTOCOL_BLOCK.rstrip() + "\n"
        else:
            before_compiled = before_compiled.rstrip() + "\n\n" + PROTOCOL_BLOCK.rstrip() + "\n"
    new_text = before_compiled.rstrip() + "\n\n" + compiled.lstrip() if compiled else before_compiled
    changed = new_text != text
    if changed:
        path.write_text(new_text, encoding="utf-8")
    return {"path": str(path), "changed": changed}


def ensure_memory_budget(hermes_home: Path, *, consolidate: bool) -> dict[str, Any]:
    mem_dir = hermes_home / "memories"
    path = mem_dir / "MEMORY.md"
    mem_dir.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("", encoding="utf-8")
    text = path.read_text(encoding="utf-8")
    limit = 2200
    target = limit // 2
    result: dict[str, Any] = {"path": str(path), "chars": len(text), "limit": limit, "changed": False}
    if len(text) <= target:
        return result
    result["over_budget"] = True
    if not consolidate:
        result["warning"] = "MEMORY.md over 50%; not consolidated because --consolidate-memory was not set"
        return result
    backup_dir = mem_dir / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / f"MEMORY-{utc_now().replace(':', '').replace('-', '')}.md"
    backup.write_text(text, encoding="utf-8")
    path.write_text(BOOTSTRAP_MEMORY, encoding="utf-8")
    result.update({"changed": True, "backup": str(backup), "chars_after": len(BOOTSTRAP_MEMORY)})
    return result


def ensure_acervo_index(acervo: Path, repo_root: Path) -> dict[str, Any]:
    dst = acervo / "global" / "tools" / "acervo_hindsight_index.py"
    src = repo_root / "acervo" / "global" / "tools" / "acervo_hindsight_index.py"
    state = acervo / "global" / "tools" / "state" / "acervo_hindsight_index.json"
    result: dict[str, Any] = {"path": str(dst), "state": str(state), "changed": False}
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or dst.read_text(encoding="utf-8", errors="replace") != src.read_text(encoding="utf-8", errors="replace"):
            shutil.copy2(src, dst)
            dst.chmod(0o755)
            result["changed"] = True
    elif not dst.exists():
        result["warning"] = f"AcervoIndex source missing: {src}"
    state.parent.mkdir(parents=True, exist_ok=True)
    if not state.exists():
        write_json(state, {"version": 1, "indexed_at": None, "entries": {}})
        result["state_created"] = True
    return result


def run_index_scan(acervo: Path, microverso: str | None, *, global_scope: bool = False) -> dict[str, Any]:
    script = acervo / "global" / "tools" / "acervo_hindsight_index.py"
    if not script.exists():
        return {"skipped": True, "reason": "missing AcervoIndex script"}
    cmd = [sys.executable, str(script), "scan"]
    if global_scope:
        cmd += ["--global"]
    elif microverso:
        cmd += ["--microverso", microverso]
    else:
        cmd += ["--all"]
    env = os.environ.copy()
    env["ACERVO"] = str(acervo)
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, env=env)
    return {"cmd": cmd, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Provision Exocortex/Hermes memory routing")
    p.add_argument("--hermes-home", default=os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))
    p.add_argument("--acervo", default=os.environ.get("ACERVO") or os.environ.get("EXOCORTEX_HOME", str(Path.home() / "exocortex")) + "/acervo")
    p.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
    p.add_argument("--microverso", default="exocortex-ops")
    p.add_argument("--scan-global", action="store_true", help="scan global Acervo layer before the selected microverso")
    p.add_argument("--skip-micro-scan", action="store_true", help="only scan global layer when paired with --scan-global")
    p.add_argument("--scan-all", action="store_true", help="scan all Acervo scopes instead of targeted canonical scopes")
    p.add_argument("--consolidate-memory", action="store_true")
    p.add_argument("--skip-index-scan", action="store_true")
    p.add_argument("--json", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    hermes_home = Path(args.hermes_home).expanduser().resolve()
    acervo = Path(args.acervo).expanduser().resolve()
    repo_root = Path(args.repo_root).expanduser().resolve()
    report: dict[str, Any] = {"ok": True, "hermes_home": str(hermes_home), "acervo": str(acervo)}
    for key, fn in [
        ("hindsight", lambda: ensure_hindsight_config(hermes_home)),
        ("hermes_memory", lambda: ensure_hermes_memory_flags(hermes_home)),
        ("soul", lambda: patch_soul(hermes_home)),
        ("memory_budget", lambda: ensure_memory_budget(hermes_home, consolidate=args.consolidate_memory)),
        ("acervo_index", lambda: ensure_acervo_index(acervo, repo_root)),
    ]:
        try:
            report[key] = fn()
        except Exception as exc:
            report["ok"] = False
            report[key] = {"error": str(exc)}
    if not args.skip_index_scan:
        scans = []
        if args.scan_all:
            scans.append(run_index_scan(acervo, None))
        else:
            if args.scan_global:
                scans.append(run_index_scan(acervo, None, global_scope=True))
            if not args.skip_micro_scan:
                scans.append(run_index_scan(acervo, args.microverso))
        report["index_scan"] = scans if len(scans) != 1 else scans[0]
        if any(scan.get("returncode", 0) != 0 for scan in scans):
            report["ok"] = False
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
