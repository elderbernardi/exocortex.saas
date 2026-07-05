#!/usr/bin/env python3
"""Core local de mutação semântica do Acervo.

Objetivo: concentrar a autoridade operacional de escritas agentic canônicas sem
acoplar a semântica ao transporte (CLI/MCP). O filesystem continua sendo a
verdade física; este módulo governa prepare/commit/validate/index/log.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from exocortex_runtime_guard import guard_write_path, resolve_acervo_root as runtime_resolve_acervo_root
from exocortex_runtime_guard import resolve_active_microverso as runtime_resolve_active_microverso

REPO_ROOT = Path(__file__).resolve().parent.parent
_SELF_DIR = Path(__file__).resolve().parent


def _resolve_helper(name: str, repo_rel: str) -> Path:
    """Locate a helper script whether the control plane runs from the repo `scripts/`
    dir or is deployed into the Acervo's `global/tools/` (where REPO_ROOT-relative paths
    would point outside the acervo). Sibling first, then the repo-relative fallback."""
    for cand in (_SELF_DIR / name, REPO_ROOT / repo_rel):
        if cand.is_file():
            return cand
    return REPO_ROOT / repo_rel


FRONTMATTER_VALIDATOR = _resolve_helper("validate_frontmatter.py", "scripts/validate_frontmatter.py")
LOG_VALIDATOR = _resolve_helper("validate_log.py", "scripts/validate_log.py")
MICROVERSO_PACKAGE = _resolve_helper("microverso_package.py", "acervo/global/tools/microverso_package.py")


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
    elif entry_type in ("UPDATED", "SUPERSEDED", "DISPUTED"):
        # SUPERSEDED/DISPUTED: memory-v2 conflict protocol (08-write-policy §4);
        # callers pass description="superseded by <rel>" / "disputed by <rel>"
        # (format enforced by validate_log.py §2).
        entry = f"- {entry_type}: {relative_output} — {description}"
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
    source_trust: str = "agent",
) -> dict[str, Any]:
    _require_trust_level(source_trust)
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
    receipt = build_receipt(
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
    receipt["source_trust"] = source_trust
    return receipt


def commit_write(
    prepared: dict[str, Any],
    *,
    content: str,
    entry_type: str,
    description: str,
    class_name: str = "volátil",
    source_trust: str | None = None,
) -> dict[str, Any]:
    target_path = Path(prepared["target_path"]).resolve()
    index_path = Path(prepared["index_path"]).resolve()
    log_path = Path(prepared["log_path"]).resolve()
    acervo_root = resolve_acervo_root(prepared["acervo_root"])
    microverso = prepared["microverso"]
    nature = prepared["nature"]

    # Trust gate (08-write-policy §2): trust travels in the receipt from
    # prepare-time; an explicit commit-time override may only tighten it.
    effective_trust = source_trust or prepared.get("source_trust") or "agent"
    _require_trust_level(effective_trust)
    require_no_secrets(content, where=f"commit_write:{prepared.get('relative_output')}")
    trust_gate: dict[str, Any] = {"source_trust": effective_trust, "forced_draft": False}
    if effective_trust == "untrusted":
        content = fm_set_scalar(content, "status", "draft")
        trust_gate["forced_draft"] = True
        trust_gate["reason"] = (
            "TRUST GATE (08-write-policy §2): conteúdo de fonte não confiável "
            "nunca vira memória ativa silenciosamente — status: draft até "
            "aprovação do executivo ou de agente verificador."
        )

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
    receipt["trust_gate"] = trust_gate
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


# ═════════════════════════════════════════════════════════════════════════
# Write pipeline v2 — conflict protocol + typed objects + trust gate
# (docs/plans/2026-07-03_memory-v2-spec/08-write-policy.md; Phase 2 of the
#  roadmap). Verbs: conflict_check / apply_supersede / open_dispute /
#  new_object. All deterministic — the dispute-vs-coexist judgment call
#  belongs to the agent (skill) reading conflict_check output, never here.
# ═════════════════════════════════════════════════════════════════════════

TRUST_LEVELS = ("executive", "agent", "untrusted")
TITLE_SIMILARITY_THRESHOLD = 0.6
SHARED_TAGS_THRESHOLD = 2
IMMUTABLE_CANON_TYPES = {"decision", "contract"}  # perene + these = dispute, never supersede
NO_LLM_NOTE = (
    "Classificação determinística (sem LLM). Verdicts: 'enrich' (mesmo path), "
    "'supersession' (candidato já aponta supersedes:) e 'overlap' (sinais). "
    "A escolha entre dispute e coexist para um 'overlap' é julgamento do "
    "agente/skill que lê esta saída (08-write-policy §4)."
)

# Defaults per new object type (05-object-model §3).
NEW_OBJECT_TYPES: dict[str, dict[str, str]] = {
    "episode": {"class": "perene", "epistemic": "observation", "nature": "episodes"},
    "entity": {"class": "perene", "epistemic": "observation", "nature": "entities"},
    "intention": {"class": "volátil", "epistemic": "intention", "nature": "intentions"},
}

_TITLE_STOPWORDS = {
    "a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "em", "no",
    "na", "nos", "nas", "um", "uma", "para", "por", "com", "sobre", "ate",
    "the", "of", "and", "to", "in", "on", "for", "with",
}


def _require_trust_level(value: str) -> None:
    if value not in TRUST_LEVELS:
        raise RuntimeError(
            f"source_trust inválido: {value!r} (esperado: {', '.join(TRUST_LEVELS)})"
        )


def load_tool_module(acervo_root: str | Path, name: str):
    """Load a Plane-2 tool from acervo/global/tools (tools live inside the Acervo)."""
    candidates = [
        Path(acervo_root) / "global" / "tools" / f"{name}.py",
        REPO_ROOT / "acervo" / "global" / "tools" / f"{name}.py",
    ]
    for candidate in candidates:
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location(name, candidate)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise RuntimeError(f"{name}.py não encontrado em global/tools.")


_VALIDATOR_MODULE = None


def _validator_module():
    """Import scripts/validate_frontmatter.py once (source of the V2-060 patterns)."""
    global _VALIDATOR_MODULE
    if _VALIDATOR_MODULE is None:
        spec = importlib.util.spec_from_file_location(
            "validate_frontmatter", FRONTMATTER_VALIDATOR
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _VALIDATOR_MODULE = module
    return _VALIDATOR_MODULE


def scan_secrets(text: str) -> list[str]:
    """V2-060 patterns over raw text; masked/redacted forms are tolerated."""
    vf = _validator_module()
    hits: list[str] = []
    for line in text.splitlines():
        for name, pattern in vf.V2_SECRET_PATTERNS:
            if name in hits:
                continue
            for match in pattern.finditer(line):
                if not vf._v2_secret_is_masked(line, match):
                    hits.append(name)
                    break
    return hits


def require_no_secrets(text: str, *, where: str) -> None:
    hits = scan_secrets(text)
    if hits:
        raise RuntimeError(
            f"V2-060 trust gate: string com formato de segredo detectada "
            f"({', '.join(hits)}) — escrita recusada em {where}. "
            f"Remova ou mascare antes de commitar."
        )


# ---------------------------------------------------------------- frontmatter


def parse_object_text(text: str) -> tuple[dict[str, Any], str]:
    """Split + parse YAML frontmatter. Raises if the block is absent/broken."""
    if not text.startswith("---\n"):
        raise RuntimeError("Arquivo sem bloco de frontmatter (--- ... ---).")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise RuntimeError("Frontmatter sem delimitador de fechamento '---'.")
    data = yaml.safe_load(text[4:end])
    if not isinstance(data, dict):
        raise RuntimeError("Frontmatter não é um mapeamento YAML.")
    return data, text[end + 5:]


def read_object(path: str | Path) -> tuple[dict[str, Any], str, str]:
    text = Path(path).read_text(encoding="utf-8")
    fm, body = parse_object_text(text)
    return fm, body, text


def _fm_lines(text: str) -> tuple[list[str], int]:
    """Return (lines, index-of-closing-'---') for a frontmattered document."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        raise RuntimeError("Arquivo sem bloco de frontmatter (--- ... ---).")
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines, i
    raise RuntimeError("Frontmatter sem delimitador de fechamento '---'.")


def fm_set_scalar(text: str, key: str, value: str) -> str:
    """Set/replace a top-level scalar frontmatter field, textually (surgical:
    everything else in the file is preserved byte-exact — no YAML re-dump)."""
    lines, end = _fm_lines(text)
    key_re = re.compile(rf"^{re.escape(key)}\s*:")
    for i in range(1, end):
        if key_re.match(lines[i]):
            lines[i] = f"{key}: {value}"
            return "\n".join(lines)
    lines.insert(end, f"{key}: {value}")
    return "\n".join(lines)


def fm_append_list(text: str, key: str, item: str) -> str:
    """Append `item` to a top-level list field (inline or block), creating the
    field if absent. Textual/surgical, no duplicate entries."""
    lines, end = _fm_lines(text)
    key_re = re.compile(rf"^{re.escape(key)}\s*:(.*)$")
    for i in range(1, end):
        match = key_re.match(lines[i])
        if not match:
            continue
        rest = match.group(1).strip()
        if rest.startswith("["):  # inline list
            items = [str(x) for x in (yaml.safe_load(rest) or [])]
            if item in items:
                return text
            items.append(item)
            lines[i] = f"{key}: [{', '.join(items)}]"
            return "\n".join(lines)
        if rest in ("", "null", "~"):  # block list (or empty/null scalar)
            insert_at = i + 1
            j = i + 1
            while j < end and lines[j].startswith((" ", "\t")):
                if lines[j].lstrip().startswith("- "):
                    if lines[j].lstrip()[2:].strip().strip("\"'") == item:
                        return text
                    insert_at = j + 1
                j += 1
            if rest in ("null", "~"):
                lines[i] = f"{key}:"
            lines.insert(insert_at, f"  - {item}")
            return "\n".join(lines)
        # scalar single value → convert to inline list
        if rest.strip("\"'") == item:
            return text
        lines[i] = f"{key}: [{rest}, {item}]"
        return "\n".join(lines)
    lines.insert(end, f"{key}:")
    lines.insert(end + 1, f"  - {item}")
    return "\n".join(lines)


def _yaml_scalar(value: str) -> str:
    """One YAML scalar, safe-quoted when needed (for generated frontmatter)."""
    dumped = yaml.safe_dump(value, allow_unicode=True, width=10_000).strip()
    if dumped.endswith("\n..."):
        dumped = dumped[:-4].strip()
    return dumped


# ---------------------------------------------------------------- similarity


def _fold(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", ascii_only).strip().casefold()


def _title_tokens(title: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9]+", _fold(title or ""))
    # Pure-number tokens vary exactly when a fact supersedes another
    # (prices, dates) — they carry no identity signal for overlap.
    return {t for t in tokens if t not in _TITLE_STOPWORDS and not t.isdigit()}


def title_similarity(a: str, b: str) -> float:
    """Token overlap coefficient |A∩B| / min(|A|,|B|) — forgiving to the
    'same subject, new value' pattern that supersession produces."""
    ta, tb = _title_tokens(a), _title_tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / min(len(ta), len(tb))


def _norm_link_target(target: str) -> str:
    t = str(target).strip().strip("\"'")
    if t.startswith("acervo/"):
        t = t[len("acervo/"):]
    if not t.endswith(".md"):
        t += ".md"
    return t


# ---------------------------------------------------------------- containers


def container_of(acervo_root: Path, rel: str) -> Path:
    """Canonical container dir (owner of _meta/) for an acervo-relative path."""
    parts = rel.split("/")
    if parts[0] == "micro" and len(parts) >= 3:
        return acervo_root / "micro" / parts[1]
    if parts[0] in ("global", "shared"):
        return acervo_root / parts[0]
    raise RuntimeError(f"Fora dos containers canônicos (micro/global/shared): {rel}")


def _meta_template(kind: str, name: str, ts: datetime) -> str:
    title = ("Índice" if kind == "index" else "Log") + f" — {name}"
    desc = (
        "Índice (MOC) do container. Gerado/atualizado pelo control plane."
        if kind == "index"
        else "Registro cronológico de eventos de ciclo de vida. Append-only."
    )
    head = f"# {title}\n" if kind == "index" else f"# Log — {name}\n"
    return (
        "---\n"
        "schema: acervo/v0.2\n"
        "type: context\n"
        f"title: {_yaml_scalar(title)}\n"
        f"description: {_yaml_scalar(desc)}\n"
        "tags: []\n"
        f"created_at: {ts.strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        "class: perene\n"
        "status: active\n"
        "epistemic: fact\n"
        "confidence: high\n"
        "sources: [{type: agent-inference, ref: \"acervoctl://ensure-meta\"}]\n"
        f"observed_at: {ts.strftime('%Y-%m-%d')}\n"
        "extraction: pipeline\n"
        "nature: _meta\n"
        "---\n\n"
        + head
    )


def ensure_container_meta(container: Path) -> dict[str, Path]:
    """Lazily create _meta/index.md + _meta/log.md (P9: nothing exists until
    first needed). Existing files are never touched."""
    meta = container / "_meta"
    meta.mkdir(parents=True, exist_ok=True)
    ts = now_utc()
    index_path = meta / "index.md"
    log_path = meta / "log.md"
    if not index_path.exists():
        index_path.write_text(_meta_template("index", container.name, ts), encoding="utf-8")
    if not log_path.exists():
        log_path.write_text(_meta_template("log", container.name, ts), encoding="utf-8")
    return {"index_path": index_path, "log_path": log_path}


def catalog_upsert(acervo_root: Path, *paths: Path) -> list[dict[str, Any]]:
    catalog = load_tool_module(acervo_root, "acervo_catalog")
    return [catalog.upsert_file(acervo_root, path) for path in paths]


def _rel_inside(acervo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(acervo_root.resolve()).as_posix()
    except ValueError:
        raise RuntimeError(f"Arquivo fora do Acervo: {path}")


class _AtomicBatch:
    """Write-all-or-nothing: snapshot originals, roll back on any failure."""

    def __init__(self) -> None:
        self._originals: dict[Path, str | None] = {}

    def snapshot(self, path: Path) -> None:
        path = path.resolve()
        if path not in self._originals:
            self._originals[path] = (
                path.read_text(encoding="utf-8") if path.exists() else None
            )

    def rollback(self) -> None:
        for path, original in self._originals.items():
            if original is None:
                path.unlink(missing_ok=True)
            else:
                path.write_text(original, encoding="utf-8")


# ---------------------------------------------------------------- conflict-check


def conflict_check(
    *,
    acervo_root: str | Path | None = None,
    candidate_path: str | Path | None = None,
    candidate_text: str | None = None,
    scope: str | None = None,
) -> dict[str, Any]:
    """Deterministic overlap detection of a candidate object vs status:active
    objects in the same scope (catalog-backed). NO LLM calls — see NO_LLM_NOTE."""
    root = resolve_acervo_root(acervo_root)
    candidate_rel: str | None = None
    if candidate_text is None:
        if candidate_path is None:
            raise RuntimeError("Informe candidate_path ou candidate_text.")
        cand = Path(candidate_path).expanduser().resolve()
        candidate_text = cand.read_text(encoding="utf-8")
        try:
            candidate_rel = cand.relative_to(root.resolve()).as_posix()
        except ValueError:
            candidate_rel = None  # draft outside the acervo — fine
    fm, _body = parse_object_text(candidate_text)

    if scope is None and candidate_rel:
        parts = candidate_rel.split("/")
        scope = parts[1] if parts[0] == "micro" and len(parts) > 1 else "global"
    if not scope:
        raise RuntimeError("Escopo não resolvido: informe --scope (micro slug ou 'global').")

    catalog = load_tool_module(root, "acervo_catalog")
    db = catalog.catalog_path(root)
    if not db.exists():
        raise RuntimeError(f"Catálogo ausente: {db} — rode `acervoctl reindex` antes.")
    conn = catalog.connect(root, create=False)
    try:
        if scope == "global":
            rows = conn.execute(
                "SELECT * FROM objects WHERE status = 'active' "
                "AND microverso IN ('global', 'shared')"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM objects WHERE status = 'active' AND microverso = ?",
                (scope,),
            ).fetchall()
        entity_links: dict[str, set[str]] = {}
        for link in conn.execute(
            "SELECT src_path, target FROM links WHERE kind = 'entity'"
        ).fetchall():
            entity_links.setdefault(link["src_path"], set()).add(str(link["target"]))
    finally:
        conn.close()

    cand_entities = {str(e) for e in (fm.get("entities") or [])}
    cand_tags = {_fold(str(t)) for t in (fm.get("tags") or [])}
    cand_title = str(fm.get("title") or "")
    cand_supersedes = {_norm_link_target(t) for t in (fm.get("supersedes") or [])}

    overlaps: list[dict[str, Any]] = []
    for row in rows:
        path = row["path"]
        if "/_meta/" in f"/{path}":
            continue
        shared_entities = sorted(cand_entities & entity_links.get(path, set()))
        row_tags = {_fold(str(t)) for t in json.loads(row["tags"] or "[]")}
        shared_tags = sorted(cand_tags & row_tags)
        similarity = round(title_similarity(cand_title, row["title"] or ""), 3)
        signals: dict[str, Any] = {}
        if shared_entities:
            signals["shared_entities"] = shared_entities
        if len(shared_tags) >= SHARED_TAGS_THRESHOLD:
            signals["shared_tags"] = shared_tags
        if similarity >= TITLE_SIMILARITY_THRESHOLD:
            signals["title_similarity"] = similarity
        if not signals:
            continue
        signals.setdefault("title_similarity", similarity)
        if candidate_rel is not None and path == candidate_rel:
            verdict = "enrich"
        elif path in cand_supersedes:
            verdict = "supersession"
        else:
            verdict = "overlap"
        overlaps.append({"path": path, "verdict": verdict, "signals": signals})

    order = {"enrich": 0, "supersession": 1, "overlap": 2}
    overlaps.sort(
        key=lambda o: (order[o["verdict"]], -o["signals"]["title_similarity"], o["path"])
    )
    return {
        "ok": True,
        "operation": "conflict_check",
        "candidate": candidate_rel or str(candidate_path or "<stdin>"),
        "scope": scope,
        "count": len(overlaps),
        "overlaps": overlaps,
        "note": NO_LLM_NOTE,
    }


# ---------------------------------------------------------------- apply-supersede


def apply_supersede(
    *,
    acervo_root: str | Path | None = None,
    new_path: str | Path,
    old_path: str | Path,
) -> dict[str, Any]:
    """Atomic supersession pairing (08 §3/§4 verb 2): old → status: superseded
    + superseded_by; new → supersedes += old. Both writes or neither."""
    root = resolve_acervo_root(acervo_root)
    new_abs = Path(new_path).expanduser().resolve()
    old_abs = Path(old_path).expanduser().resolve()
    for label, path in (("--new", new_abs), ("--old", old_abs)):
        if not path.is_file():
            raise RuntimeError(f"Arquivo {label} não encontrado: {path}")
    new_rel = _rel_inside(root, new_abs)
    old_rel = _rel_inside(root, old_abs)
    if new_rel == old_rel:
        raise RuntimeError("--new e --old apontam para o mesmo arquivo.")

    old_fm, _, old_text = read_object(old_abs)
    _new_fm, _, new_text = read_object(new_abs)

    if old_fm.get("class") == "perene" and str(old_fm.get("type")) in IMMUTABLE_CANON_TYPES:
        raise RuntimeError(
            f"Recusado: {old_rel} é cânone imutável (class: perene, type: "
            f"{old_fm.get('type')}). Mudança de decisão/contrato exige disputa "
            f"explícita — use `acervoctl open-dispute` (08-write-policy §4.3)."
        )
    if old_fm.get("status") == "superseded" or old_fm.get("superseded_by"):
        raise RuntimeError(
            f"Recusado: {old_rel} já está superseded "
            f"(superseded_by: {old_fm.get('superseded_by')})."
        )

    new_text2 = fm_append_list(new_text, "supersedes", old_rel)
    old_text2 = fm_set_scalar(
        fm_set_scalar(old_text, "status", "superseded"), "superseded_by", new_rel
    )

    container = container_of(root, old_rel)
    batch = _AtomicBatch()
    meta_dir_existed = (container / "_meta").exists()
    try:
        batch.snapshot(old_abs)
        batch.snapshot(new_abs)
        meta = ensure_container_meta(container)
        batch.snapshot(meta["log_path"])
        old_abs.write_text(old_text2, encoding="utf-8")
        new_abs.write_text(new_text2, encoding="utf-8")
        validate_entry(old_abs)
        validate_entry(new_abs)
        append_log(
            meta["log_path"],
            relative_output=old_rel,
            ts=now_utc(),
            entry_type="SUPERSEDED",
            description=f"superseded by {new_rel}",
        )
        validate_log(meta["log_path"])
    except Exception:
        batch.rollback()
        if not meta_dir_existed:
            for name in ("index.md", "log.md"):
                (container / "_meta" / name).unlink(missing_ok=True)
        raise

    upserts = catalog_upsert(root, old_abs, new_abs)
    return {
        "ok": True,
        "operation": "apply_supersede",
        "old": old_rel,
        "new": new_rel,
        "log_path": str(meta["log_path"]),
        "catalog": upserts,
    }


# ---------------------------------------------------------------- open-dispute


def open_dispute(
    *,
    acervo_root: str | Path | None = None,
    a_path: str | Path,
    b_path: str | Path,
    title: str,
    scope: str,
) -> dict[str, Any]:
    """Create a first-class conflict object (05 §3, examples.md #6) and stamp
    disputed_by on both sides. Atomic: all three writes or none."""
    root = resolve_acervo_root(acervo_root)
    a_abs = Path(a_path).expanduser().resolve()
    b_abs = Path(b_path).expanduser().resolve()
    for label, path in (("--a", a_abs), ("--b", b_abs)):
        if not path.is_file():
            raise RuntimeError(f"Arquivo {label} não encontrado: {path}")
    a_rel = _rel_inside(root, a_abs)
    b_rel = _rel_inside(root, b_abs)
    if a_rel == b_rel:
        raise RuntimeError("--a e --b apontam para o mesmo arquivo.")

    a_fm, _, a_text = read_object(a_abs)
    b_fm, _, b_text = read_object(b_abs)
    for rel, fm in ((a_rel, a_fm), (b_rel, b_fm)):
        if fm.get("disputed_by"):
            raise RuntimeError(f"Recusado: {rel} já está em disputa ({fm['disputed_by']}).")

    if scope == "global":
        scope_root = root / "global"
    else:
        scope_root = root / "micro" / scope
        if not scope_root.is_dir():
            raise RuntimeError(f"Microverso inexistente: {scope_root}")
    slug = slugify(title)
    if not slug.startswith("conflito"):
        slug = f"conflito-{slug}"
    conflict_abs = (scope_root / "knowledge" / f"{slug}.md").resolve()
    conflict_rel = conflict_abs.relative_to(root.resolve()).as_posix()
    if conflict_abs.exists():
        raise RuntimeError(f"Objeto de conflito já existe: {conflict_rel}")

    ts = now_utc()

    def _claim(letter: str, rel: str, fm: dict[str, Any]) -> str:
        return (
            f"**Claim {letter} ({rel}, observed_at: {fm.get('observed_at')}, "
            f"confidence: {fm.get('confidence')}):** {fm.get('title')}"
        )

    description = f"Disputa aberta entre {Path(a_rel).stem} e {Path(b_rel).stem}"
    if len(description) > 160:
        description = description[:157] + "..."
    conflict_text = (
        "---\n"
        "schema: acervo/v0.2\n"
        "type: conflict\n"
        f"title: {_yaml_scalar(title)}\n"
        f"description: {_yaml_scalar(description)}\n"
        "tags: [conflito]\n"
        f"created_at: {ts.strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        "class: volátil\n"
        "status: active\n"
        "epistemic: hypothesis\n"
        "confidence: possible\n"
        "sources:\n"
        f"  - {{type: document, ref: \"{a_rel}\"}}\n"
        f"  - {{type: document, ref: \"{b_rel}\"}}\n"
        f"observed_at: {ts.strftime('%Y-%m-%d')}\n"
        "extraction: agent\n"
        "relates_to:\n"
        f"  - {a_rel}\n"
        f"  - {b_rel}\n"
        "---\n\n"
        f"{_claim('A', a_rel, a_fm)}\n\n"
        f"{_claim('B', b_rel, b_fm)}\n\n"
        "**Aguardando resolução do executivo** (digest de manutenção carrega "
        "disputas abertas — 08-write-policy §4.3).\n"
    )
    require_no_secrets(conflict_text, where=f"open_dispute:{conflict_rel}")

    a_text2 = fm_set_scalar(a_text, "disputed_by", conflict_rel)
    b_text2 = fm_set_scalar(b_text, "disputed_by", conflict_rel)

    containers = {container_of(root, rel) for rel in (conflict_rel, a_rel, b_rel)}
    batch = _AtomicBatch()
    created_meta_dirs = [c for c in containers if not (c / "_meta").exists()]
    try:
        batch.snapshot(conflict_abs)
        batch.snapshot(a_abs)
        batch.snapshot(b_abs)
        metas = {c: ensure_container_meta(c) for c in containers}
        for meta in metas.values():
            batch.snapshot(meta["log_path"])
            batch.snapshot(meta["index_path"])
        conflict_abs.parent.mkdir(parents=True, exist_ok=True)
        conflict_abs.write_text(conflict_text, encoding="utf-8")
        a_abs.write_text(a_text2, encoding="utf-8")
        b_abs.write_text(b_text2, encoding="utf-8")
        validate_entry(conflict_abs)
        validate_entry(a_abs)
        validate_entry(b_abs)

        conflict_meta = metas[container_of(root, conflict_rel)]
        append_log(
            conflict_meta["log_path"], relative_output=conflict_rel, ts=ts,
            entry_type="CREATED", description=description, class_name="volátil",
        )
        update_index(conflict_meta["index_path"], conflict_rel, "knowledge")
        for rel in (a_rel, b_rel):
            meta = metas[container_of(root, rel)]
            append_log(
                meta["log_path"], relative_output=rel, ts=ts,
                entry_type="DISPUTED", description=f"disputed by {conflict_rel}",
            )
        for meta in metas.values():
            validate_log(meta["log_path"])
    except Exception:
        batch.rollback()
        for container in created_meta_dirs:
            for name in ("index.md", "log.md"):
                (container / "_meta" / name).unlink(missing_ok=True)
        raise

    upserts = catalog_upsert(root, conflict_abs, a_abs, b_abs)
    return {
        "ok": True,
        "operation": "open_dispute",
        "conflict": conflict_rel,
        "a": a_rel,
        "b": b_rel,
        "catalog": upserts,
    }


# ---------------------------------------------------------------- new-object


def _short_title_slug(title: str) -> str:
    """Slug of the identity portion of a title (before ' — ' qualifiers)."""
    head = re.split(r"—|,", title, maxsplit=1)[0].strip()
    return slugify(head or title)


def iter_entity_files(acervo_root: Path):
    """Every canonical entity page (Plane 1 is the truth for the no-dup gate)."""
    for pattern in ("shared/entities/*.md", "micro/*/entities/*.md"):
        yield from sorted(acervo_root.glob(pattern))


def find_entity_alias_dup(
    acervo_root: Path, aliases: list[str], title: str | None = None
) -> dict[str, Any] | None:
    """Case/accent-folded match of candidate aliases (+title) against every
    existing entity's aliases + title. Returns the collision or None."""
    needles = {_fold(a) for a in aliases if a and a.strip()}
    if title:
        needles.add(_fold(title))
        needles.add(_fold(re.split(r"—|,", title, maxsplit=1)[0]))
    needles.discard("")
    for path in iter_entity_files(acervo_root):
        try:
            fm, _body = parse_object_text(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        haystack = {_fold(str(a)) for a in (fm.get("aliases") or [])}
        existing_title = str(fm.get("title") or "")
        haystack.add(_fold(existing_title))
        haystack.add(_fold(re.split(r"—|,", existing_title, maxsplit=1)[0]))
        haystack.discard("")
        matched = sorted(needles & haystack)
        if matched:
            return {
                "path": path.relative_to(acervo_root).as_posix(),
                "matched": matched,
            }
    return None


def _hindsight_index_best_effort(acervo_root: Path, target: Path) -> dict[str, Any]:
    """Existing hook pattern (acervoctl reindex): best-effort, never fatal."""
    indexer = Path(acervo_root) / "global" / "tools" / "acervo_hindsight_index.py"
    if not indexer.is_file():
        indexer = REPO_ROOT / "acervo" / "global" / "tools" / "acervo_hindsight_index.py"
    if not indexer.is_file():
        return {"attempted": False, "reason": "indexer not found"}
    try:
        proc = subprocess.run(
            [sys.executable, str(indexer), "index-file", str(target)],
            capture_output=True, text=True, timeout=30,
            env={**os.environ, "ACERVO": str(acervo_root)},
        )
        return {
            "attempted": True,
            "exit_code": proc.returncode,
            "output": proc.stdout.strip()[-1000:],
            "stderr": proc.stderr.strip()[-500:],
        }
    except Exception as exc:  # restricted env / no Hindsight — never fatal
        return {"attempted": True, "error": str(exc)}


def new_object(
    *,
    acervo_root: str | Path | None = None,
    type_: str,
    scope: str,
    title: str,
    description: str | None = None,
    aliases: list[str] | None = None,
    due: str | None = None,
    trigger: str | None = None,
    owed_to: str | None = None,
    tags: list[str] | None = None,
    entities: list[str] | None = None,
    body: str | None = None,
    draft: bool = False,
    source_trust: str = "agent",
) -> dict[str, Any]:
    """Scaffold a schema-v0.2-valid episode/entity/intention in the right
    nature dir (lazy creation — P9), with trust gate + secret scan + journal
    + catalog upsert + best-effort Hindsight index."""
    if type_ not in NEW_OBJECT_TYPES:
        raise RuntimeError(
            f"type inválido: {type_!r} (new-object cobre: {', '.join(NEW_OBJECT_TYPES)})"
        )
    _require_trust_level(source_trust)
    root = resolve_acervo_root(acervo_root)
    defaults = NEW_OBJECT_TYPES[type_]
    nature = defaults["nature"]
    ts = now_utc()

    # Type-specific gates BEFORE any filesystem effect.
    if type_ == "intention" and not (due or trigger):
        raise RuntimeError(
            "Recusado: intention exige --due ou --trigger (memória prospectiva "
            "sem gatilho nunca dispara — 05-object-model §3)."
        )
    if type_ == "entity":
        aliases = [a.strip() for a in (aliases or []) if a and a.strip()]
        if not aliases:
            raise RuntimeError(
                "Recusado: entity exige --aliases (aliases: é obrigatório — V2-050; "
                "é o que torna a página encontrável)."
            )
        dup = find_entity_alias_dup(root, aliases, title)
        if dup:
            raise RuntimeError(
                f"Recusado: entidade já existe em {dup['path']} "
                f"(match de alias/título: {', '.join(dup['matched'])}). "
                f"Enriqueça a página existente em vez de duplicar (08 §7.9)."
            )
    if due and not re.match(r"^\d{4}-\d{2}-\d{2}$", due):
        raise RuntimeError(f"--due deve ser YYYY-MM-DD, recebido: {due!r}")

    # Target path (lazy dirs — P9). Entities in scope 'global' live in the
    # shared/ registry (05 §3); everything else global lives under global/.
    if type_ == "entity":
        container = (root / "shared") if scope == "global" else (root / "micro" / scope)
        filename = f"{_short_title_slug(title)}.md"
    else:
        container = (root / "global") if scope == "global" else (root / "micro" / scope)
        filename = f"{ts.strftime('%Y-%m-%d')}-{slugify(title)}.md"
    if scope != "global" and not (root / "micro" / scope).is_dir():
        raise RuntimeError(f"Microverso inexistente: {root / 'micro' / scope}")
    nature_dir = container / nature
    target = (nature_dir / filename).resolve()
    if target.exists():
        raise RuntimeError(f"Arquivo já existe: {target}")
    rel = target.relative_to(root.resolve()).as_posix()

    status = "draft" if (draft or source_trust == "untrusted") else "active"
    trust_gate: dict[str, Any] = {
        "source_trust": source_trust,
        "forced_draft": source_trust == "untrusted" and not draft,
    }
    if source_trust == "untrusted":
        trust_gate["reason"] = (
            "TRUST GATE (08-write-policy §2): conteúdo de fonte não confiável "
            "nunca vira memória ativa silenciosamente — status: draft até "
            "aprovação do executivo ou de agente verificador."
        )

    source_type = {
        "executive": "executive", "agent": "agent-inference", "untrusted": "web",
    }[source_trust]
    extraction = "executive" if source_trust == "executive" else "agent"
    description = (description or title).strip()
    if len(description) > 160:
        description = description[:157] + "..."

    fm_lines = [
        "---",
        "schema: acervo/v0.2",
        f"type: {type_}",
        f"title: {_yaml_scalar(title)}",
        f"description: {_yaml_scalar(description)}",
        f"tags: [{', '.join(str(t) for t in (tags or []))}]",
        f"created_at: {ts.strftime('%Y-%m-%dT%H:%M:%SZ')}",
        f"class: {defaults['class']}",
        f"status: {status}",
        f"epistemic: {defaults['epistemic']}",
        "confidence: high",
        f"sources: [{{type: {source_type}, ref: \"acervoctl://new-object\"}}]",
        f"observed_at: {ts.strftime('%Y-%m-%d')}",
        f"extraction: {extraction}",
    ]
    if entities:
        fm_lines.append(f"entities: [{', '.join(entities)}]")
    if type_ == "entity":
        fm_lines.append(
            "aliases: [" + ", ".join(_yaml_scalar(a) for a in aliases) + "]"
        )
    if type_ == "intention":
        if due:
            fm_lines.append(f"due: {due}")
        if trigger:
            fm_lines.append(f"trigger: {_yaml_scalar(trigger)}")
        if owed_to:
            fm_lines.append(f"owed_to: {owed_to}")
    fm_lines.append("---")

    if body is None:
        if type_ == "entity":
            body = (
                "## Perfil          <!-- rewrite-in-place -->\n"
                f"{description}\n\n"
                "## Interações      <!-- append-only -->\n"
            )
        else:
            body = f"{description}\n"
    text = "\n".join(fm_lines) + "\n\n" + body.rstrip() + "\n"

    require_no_secrets(text, where=f"new_object:{rel}")

    # Scope guard: micro writes go through the runtime guard; global/shared
    # writes are control-plane authority (explicit acervoctl verb), contained
    # to the canonical dirs computed above.
    if scope != "global":
        guard_write_scope(target, active_microverso=scope, acervo_root=root)

    nature_dir.mkdir(parents=True, exist_ok=True)
    meta = ensure_container_meta(container)
    target.write_text(text, encoding="utf-8")
    try:
        validate_entry(target)
    except Exception:
        target.unlink(missing_ok=True)
        raise

    append_log(
        meta["log_path"], relative_output=rel, ts=ts,
        entry_type="CREATED", description=description, class_name=defaults["class"],
    )
    validate_log(meta["log_path"])
    update_index(meta["index_path"], rel, nature)
    upserts = catalog_upsert(root, target)
    hindsight = _hindsight_index_best_effort(root, target)

    return {
        "ok": True,
        "operation": "new_object",
        "type": type_,
        "scope": scope,
        "status": status,
        "target_path": str(target),
        "relative_output": rel,
        "log_path": str(meta["log_path"]),
        "index_path": str(meta["index_path"]),
        "trust_gate": trust_gate,
        "catalog": upserts,
        "hindsight": hindsight,
    }
