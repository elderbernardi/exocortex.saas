#!/usr/bin/env python3
"""Run Codex CLI with lightweight local evidence capture.

This wrapper is intentionally stdlib-only so it can live under
``~/.hermes/scripts/codex_learning/`` after setup.sh provisioning.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def hermes_home() -> Path:
    raw = os.environ.get("HERMES_HOME", "").strip()
    return Path(raw).expanduser() if raw else Path.home() / ".hermes"


def utc_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def ensure_git_repo(workdir: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=workdir, check=True)
    subprocess.run(["git", "config", "user.name", "Exocortex Smoke"], cwd=workdir, check=True)
    subprocess.run(["git", "config", "user.email", "exocortex@example.invalid"], cwd=workdir, check=True)
    readme = workdir / ".gitignore"
    if not readme.exists():
        readme.write_text(".codex/\n", encoding="utf-8")
        subprocess.run(["git", "add", ".gitignore"], cwd=workdir, check=True)
        subprocess.run(["git", "commit", "-qm", "baseline"], cwd=workdir, check=True)


def run_capture(command: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "command": shlex.join(command),
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def git_evidence(workdir: Path) -> dict[str, Any]:
    status = run_capture(["git", "status", "--porcelain"], workdir)
    diff_stat = run_capture(["git", "diff", "--stat"], workdir)
    diff_names = run_capture(["git", "diff", "--name-only"], workdir)
    untracked = run_capture(["git", "ls-files", "--others", "--exclude-standard"], workdir)
    changed_files: list[str] = []
    for line in status["stdout"].splitlines():
        if not line.strip():
            continue
        changed_files.append(line[3:] if len(line) > 3 else line)
    return {
        "git_status_porcelain": status["stdout"],
        "git_diff_stat": diff_stat["stdout"],
        "git_diff_name_only": diff_names["stdout"],
        "git_untracked_files": [line for line in untracked["stdout"].splitlines() if line.strip()],
        "changed_files": changed_files,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Codex wrapper with local run/event evidence.")
    parser.add_argument("--prompt", help="Prompt enviado ao Codex.")
    parser.add_argument("--prompt-file", help="Arquivo de prompt; usado se --prompt não for passado.")
    parser.add_argument("--cd", dest="workdir", help="Diretório alvo do run.")
    parser.add_argument("--scratch", action="store_true", help="Executa em repositório temporário com git init.")
    parser.add_argument("--full-auto", action="store_true", help="Compatibilidade legada: mapeia para --sandbox workspace-write.")
    parser.add_argument("--sandbox", default="read-only", choices=["read-only", "workspace-write", "danger-full-access"])
    parser.add_argument("--model", help="Modelo opcional para o Codex CLI.")
    parser.add_argument("--codex-bin", default=os.environ.get("CODEX_BIN", "codex"), help="Binário do Codex CLI.")
    parser.add_argument("--simulate-output", help="Smoke offline: não invoca Codex; usa este stdout sintético verificável.")
    parser.add_argument("--simulate-stderr", default="", help="Smoke offline: stderr sintético.")
    parser.add_argument("--simulate-exit", type=int, default=0, help="Smoke offline: exit code sintético.")
    return parser


def resolve_prompt(args: argparse.Namespace) -> str:
    if args.prompt:
        return args.prompt
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8")
    raise SystemExit("--prompt ou --prompt-file é obrigatório")


def main() -> int:
    args = build_parser().parse_args()
    prompt = resolve_prompt(args)

    hh = hermes_home()
    runs_dir = hh / "codex-learning" / "runs"
    events_dir = hh / "codex-learning" / "events"
    reviews_dir = hh / "codex-learning" / "reviews"
    for path in (runs_dir, events_dir, reviews_dir):
        path.mkdir(parents=True, exist_ok=True)

    sandbox = "workspace-write" if args.full_auto else args.sandbox
    run_id = utc_run_id()

    tempdir: tempfile.TemporaryDirectory[str] | None = None
    if args.scratch:
        tempdir = tempfile.TemporaryDirectory(prefix="codex-learning-")
        workdir = Path(tempdir.name)
    elif args.workdir:
        workdir = Path(args.workdir).expanduser().resolve()
        workdir.mkdir(parents=True, exist_ok=True)
    else:
        workdir = Path.cwd()

    try:
        ensure_git_repo(workdir)

        if args.simulate_output is not None:
            command = [args.codex_bin, "exec", "<simulated>"]
            exit_code = args.simulate_exit
            stdout = args.simulate_output
            stderr = args.simulate_stderr
        else:
            command = [args.codex_bin, "exec", "--skip-git-repo-check", "-s", sandbox]
            if args.model:
                command.extend(["-m", args.model])
            command.append(prompt)
            completed = subprocess.run(
                command,
                cwd=workdir,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            exit_code = completed.returncode
            stdout = completed.stdout
            stderr = completed.stderr

        evidence = git_evidence(workdir)
        payload = {
            "run_id": run_id,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "prompt": prompt,
            "command": shlex.join(command),
            "scratch": bool(args.scratch),
            "workdir": str(workdir),
            "sandbox": sandbox,
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            **evidence,
        }
        summary_path = runs_dir / f"{run_id}.summary.json"
        summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        event_path = events_dir / f"{run_id}.jsonl"
        event_path.write_text(json.dumps({
            "run_id": run_id,
            "timestamp_utc": payload["timestamp_utc"],
            "command": payload["command"],
            "exit_code": exit_code,
            "changed_files": payload["changed_files"],
        }, ensure_ascii=False) + "\n", encoding="utf-8")

        print(json.dumps({"run_id": run_id, "summary_path": str(summary_path), "event_path": str(event_path)}, ensure_ascii=False))
        return 0 if exit_code == 0 else exit_code
    finally:
        if tempdir is not None:
            tempdir.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
