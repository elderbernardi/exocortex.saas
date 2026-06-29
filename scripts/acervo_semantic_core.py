#!/usr/bin/env python3
"""Core local de mutação semântica do Acervo.

Objetivo: concentrar a autoridade operacional de escritas agentic canônicas sem
acoplar a semântica ao transporte (CLI/MCP). O filesystem continua sendo a
verdade física; este módulo governa prepare/commit/validate/index/log.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from exocortex_runtime_guard import guard_write_path, resolve_acervo_root as runtime_resolve_acervo_root
from exocortex_runtime_guard import resolve_active_microverso as runtime_resolve_active_microverso

REPO_ROOT = Path(__file__).resolve().parent.parent
FRONTMATTER_VALIDATOR = REPO_ROOT / "scripts" / "validate_frontmatter.py"
LOG_VALIDATOR = REPO_ROOT / "scripts" / "validate_log.py"
MICROVERSO_PACKAGE = REPO_ROOT / "acervo" / "global" / "tools" / "microverso_package.py"


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_only).strip("-").lower()
    return slug or "documento"


def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def resolve_acervo_root(explicit: str | Path | None = None) -> Path:
    if explicit is not None:
        return Path(explicit).expanduser().resolve()
    return runtime_resolve_acervo_root().resolve()


def resolve_active_microverso(
    active_microverso: str | None = None,
    cwd: str | Path | None = None,
    acervo_root: str | Path | None = None,
) -> str:
    return runtime_resolve_active_microverso(
        active_microverso=active_microverso,
        cwd=cwd,
        acervo_root=resolve_acervo_root(acervo_root),
    )


def relative_to_acervo(path: Path, acervo_root: Path) -> str:
    return path.resolve().relative_to(acervo_root.resolve()).as_posix()


def guard_write_scope(
    target_path: str | Path,
    *,
    active_microverso: str | None = None,
    acervo_root: str | Path | None = None,
    cwd: str | Path | None = None,
) -> dict[str, Any]:
    root = resolve_acervo_root(acervo_root)
    result = guard_write_path(
        target_path=target_path,
        active_microverso=active_microverso,
        acervo_root=root,
        cwd=cwd,
    )
    if result.get("allowed") is not True:
        raise RuntimeError(result.get("message") or json.dumps(result, ensure_ascii=False))
    return result


def ensure_microverso_structure(acervo_root: str | Path, microverso: str, nature: str) -> dict[str, Path]:
    root = resolve_acervo_root(acervo_root)
    micro_root = root / "micro" / microverso
    if not micro_root.exists():
        raise RuntimeError(f"Microverso inexistente: {micro_root}")

    nature_dir = micro_root / nature
    nature_dir.mkdir(parents=True, exist_ok=True)
    meta_dir = micro_root / "_meta"
    index_path = meta_dir / "index.md"
    log_path = meta_dir / "log.md"
    if not index_path.exists():
        raise RuntimeError(f"Índice ausente: {index_path}")
    if not log_path.exists():
        raise RuntimeError(f"Log ausente: {log_path}")
    return {
        "acervo_root": root,
        "micro_root": micro_root,
        "nature_dir": nature_dir,
        "index_path": index_path,
        "log_path": log_path,
    }


def list_microversos(acervo_root: str | Path | None = None) -> list[str]:
    root = resolve_acervo_root(acervo_root)
    micro_dir = root / "micro"
    if not micro_dir.is_dir():
        return []
    return sorted(
        child.name
        for child in micro_dir.iterdir()
        if child.is_dir() and not child.name.startswith("_")
    )


def search_acervo(acervo_root: str | Path | None, query: str, limit: int = 20) -> list[dict[str, Any]]:
    root = resolve_acervo_root(acervo_root)
    needle = query.casefold()
    matches: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        if "/.quarantine/" in rel or rel.startswith(".quarantine/"):
            continue
        if "/raw/" in rel or rel.startswith("raw/"):
            continue
        for idx, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            if needle in line.casefold():
                matches.append({"path": rel, "line_no": idx, "line": line.strip()})
                if len(matches) >= limit:
                    return matches
                break
    return matches


def _nature_heading(nature: str) -> str:
    return nature.replace("_", " ").title()


def _index_bullet(relative_output: str) -> str:
    return f"- `{relative_output}`"


def update_index(index_path: str | Path, relative_output: str, nature: str) -> None:
    path = Path(index_path)
    content = path.read_text(encoding="utf-8")
    bullet = _index_bullet(relative_output)
    if bullet in content:
        return

    heading_re = re.compile(rf"^###\s+{re.escape(_nature_heading(nature))}\b.*$", re.MULTILINE)
    match = heading_re.search(content)
    if match:
        insert_at = match.end()
        content = content[:insert_at] + "\n" + bullet + content[insert_at:]
        path.write_text(content, encoding="utf-8")
        return

    separator = "\n" if content.endswith("\n") else "\n\n"
    content += f"{separator}### {_nature_heading(nature)}\n{bullet}\n"
    path.write_text(content, encoding="utf-8")


def append_log(
    log_path: str | Path,
    *,
    relative_output: str,
    ts: datetime,
    entry_type: str,
    description: str,
    class_name: str = "volátil",
) -> None:
    entry_type = entry_type.upper()
    if entry_type == "CREATED":
        entry = f"- CREATED: {relative_output} ({class_name}) — {description}"
    elif entry_type == "UPDATED":
        entry = f"- UPDATED: {relative_output} — {description}"
    else:
        raise ValueError(f"Tipo de log não suportado neste corte: {entry_type}")

    path = Path(log_path)
    content = path.read_text(encoding="utf-8")
    if entry in content:
        return

    heading = f"## {ts.strftime('%Y-%m-%d')}"
    if heading in content:
        content = content.rstrip() + "\n" + entry + "\n"
    else:
        suffix = "\n" if content.endswith("\n") else "\n\n"
        content = content + suffix + heading + "\n" + entry + "\n"
    path.write_text(content, encoding="utf-8")


def _run_validator(command: list[str], *, path_for_error: Path) -> None:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Validação falhou para {path_for_error}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def validate_entry(path: str | Path) -> None:
    target = Path(path).resolve()
    _run_validator([sys.executable, str(FRONTMATTER_VALIDATOR), "--file", str(target)], path_for_error=target)


def validate_log(path: str | Path) -> None:
    target = Path(path).resolve()
    _run_validator([sys.executable, str(LOG_VALIDATOR), "--file", str(target)], path_for_error=target)


def build_receipt(
    *,
    status: str,
    operation: str,
    acervo_root: Path,
    microverso: str,
    nature: str,
    target_path: Path,
    index_path: Path,
    log_path: Path,
    guard_result: dict[str, Any],
    ts: datetime,
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "status": status,
        "operation": operation,
        "prepared_at": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "acervo_root": str(acervo_root),
        "microverso": microverso,
        "nature": nature,
        "target_path": str(target_path),
        "relative_output": relative_to_acervo(target_path, acervo_root),
        "index_path": str(index_path),
        "log_path": str(log_path),
        "allowed_root": guard_result.get("allowed_root"),
        "warnings": warnings or [],
    }


def prepare_write(
    *,
    acervo_root: str | Path | None,
    microverso: str,
    nature: str,
    filename: str,
    active_microverso: str | None = None,
    cwd: str | Path | None = None,
) -> dict[str, Any]:
    resolved_root = resolve_acervo_root(acervo_root)
    paths = ensure_microverso_structure(resolved_root, microverso, nature)
    target_path = paths["nature_dir"] / filename
    guard_result = guard_write_scope(
        target_path,
        active_microverso=active_microverso or microverso,
        acervo_root=paths["acervo_root"],
        cwd=cwd,
    )
    ts = now_utc()
    return build_receipt(
        status="prepared",
        operation="prepare_write",
        acervo_root=paths["acervo_root"],
        microverso=microverso,
        nature=nature,
        target_path=target_path,
        index_path=paths["index_path"],
        log_path=paths["log_path"],
        guard_result=guard_result,
        ts=ts,
    )


def commit_write(
    prepared: dict[str, Any],
    *,
    content: str,
    entry_type: str,
    description: str,
    class_name: str = "volátil",
) -> dict[str, Any]:
    target_path = Path(prepared["target_path"]).resolve()
    index_path = Path(prepared["index_path"]).resolve()
    log_path = Path(prepared["log_path"]).resolve()
    acervo_root = resolve_acervo_root(prepared["acervo_root"])
    microverso = prepared["microverso"]
    nature = prepared["nature"]

    guard_result = guard_write_scope(
        target_path,
        active_microverso=microverso,
        acervo_root=acervo_root,
    )
    target_path.write_text(content, encoding="utf-8")
    validate_entry(target_path)
    update_index(index_path, prepared["relative_output"], nature)
    append_log(
        log_path,
        relative_output=prepared["relative_output"],
        ts=now_utc(),
        entry_type=entry_type,
        description=description,
        class_name=class_name,
    )
    validate_log(log_path)
    receipt = build_receipt(
        status="committed",
        operation="commit_write",
        acervo_root=acervo_root,
        microverso=microverso,
        nature=nature,
        target_path=target_path,
        index_path=index_path,
        log_path=log_path,
        guard_result=guard_result,
        ts=now_utc(),
    )
    receipt["entry_type"] = entry_type.upper()
    return receipt


def export_microverso(
    *,
    acervo_root: str | Path | None,
    slug: str,
    out_dir: str | Path,
    tar: bool = False,
) -> dict[str, Any]:
    root = resolve_acervo_root(acervo_root)
    command = [
        sys.executable,
        str(MICROVERSO_PACKAGE),
        "--microverso",
        slug,
        "--acervo",
        str(root),
        "--out",
        str(Path(out_dir).expanduser().resolve()),
    ]
    if tar:
        command.append("--tar")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Export falhou para {slug}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )

    package_path: str | None = None
    for line in result.stdout.splitlines():
        if line.startswith("package: "):
            package_path = line.split("package: ", 1)[1].strip()
            break
    if not package_path:
        raise RuntimeError(f"Export concluiu sem package path explícito.\nstdout:\n{result.stdout}")
    return {
        "ok": True,
        "slug": slug,
        "package_path": package_path,
        "stdout": result.stdout,
    }
