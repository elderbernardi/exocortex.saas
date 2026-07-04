#!/usr/bin/env python3
"""AcervoIndex: index canonical Acervo markdown files into Hindsight.

The index stores short semantic pointers, not full Acervo content.
Principle: Hindsight points; Acervo decides.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception as exc:  # pragma: no cover
    raise SystemExit(f"PyYAML is required: {exc}")

INDEXABLE_NATURES = {
    "context",
    "knowledge",
    "decisions",
    "reflections",
    "contracts",
    "tools",
    "workflows",
}
SKIP_PARTS = {"raw", "_archive", ".quarantine", "__pycache__", "state", "_retired", "_template", "_fixture", "_inbox", "_ops_snapshots"}
DEFAULT_STATE_REL = "global/tools/state/acervo_hindsight_index.json"
MAX_SUMMARY_CHARS = 1000


@dataclass
class IndexResult:
    indexed: int = 0
    skipped_unchanged: int = 0
    skipped_lifecycle: int = 0
    skipped_not_indexable: int = 0
    errors: int = 0

    def as_dict(self) -> dict[str, int]:
        return self.__dict__.copy()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def resolve_acervo() -> Path:
    for key in ("ACERVO",):
        value = os.environ.get(key)
        if value and Path(value).expanduser().is_dir():
            return Path(value).expanduser().resolve()
    exo = os.environ.get("EXOCORTEX_HOME")
    candidates = []
    if exo:
        candidates.append(Path(exo).expanduser() / "acervo")
    candidates.extend([
        Path.home() / "exocortex" / "acervo",
        Path.home() / ".hermes" / "acervo",
    ])
    for candidate in candidates:
        if candidate.is_dir():
            return candidate.resolve()
    raise SystemExit("Acervo root not found. Set ACERVO=/path/to/acervo.")


def load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON manifest {path}: {exc}")


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        data = {}
    return data, body


def nature_from_path(acervo: Path, path: Path, fm: dict[str, Any]) -> str:
    nature = str(fm.get("nature") or "").strip()
    if nature:
        return nature
    rel_parts = path.relative_to(acervo).parts
    # micro/{slug}/{nature}/file.md or global/{nature}/file.md
    if len(rel_parts) >= 3 and rel_parts[0] == "micro":
        return rel_parts[2]
    if len(rel_parts) >= 2 and rel_parts[0] in {"global", "shared"}:
        return rel_parts[1]
    return ""


def microverso_from_path(acervo: Path, path: Path) -> str:
    parts = path.relative_to(acervo).parts
    if len(parts) >= 2 and parts[0] == "micro":
        return parts[1]
    return parts[0] if parts else "unknown"


def should_skip(acervo: Path, path: Path, fm: dict[str, Any]) -> tuple[bool, str]:
    rel_parts = set(path.relative_to(acervo).parts)
    if rel_parts & SKIP_PARTS:
        return True, "lifecycle-path"
    if fm.get("deprecated") is True or str(fm.get("deprecated", "")).lower() == "true":
        return True, "deprecated"
    nature = nature_from_path(acervo, path, fm)
    if nature not in INDEXABLE_NATURES:
        return True, "not-indexable-nature"
    return False, ""


def tags_from_frontmatter(fm: dict[str, Any]) -> list[str]:
    tags = fm.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in re.split(r"[,\s]+", tags) if t.strip()]
    if not isinstance(tags, list):
        tags = []
    out = []
    for tag in tags:
        s = str(tag).strip()
        if s and s not in out:
            out.append(s)
    return out


def first_paragraph(body: str) -> str:
    cleaned = []
    in_code = False
    for line in body.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if line.strip().startswith("#"):
            continue
        if line.strip().startswith(("- ", "* ", "|")):
            continue
        cleaned.append(line)
    text = "\n".join(cleaned)
    blocks = [re.sub(r"\s+", " ", b).strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    return blocks[0] if blocks else ""


def headings(body: str, limit: int = 6) -> list[str]:
    found = []
    for line in body.splitlines():
        m = re.match(r"^(#{2,4})\s+(.+?)\s*$", line)
        if m:
            title = re.sub(r"[#`*_]+", "", m.group(2)).strip()
            if title:
                found.append(title)
        if len(found) >= limit:
            break
    return found


def build_summary(fm: dict[str, Any], body: str) -> str:
    parts = []
    if fm.get("description"):
        parts.append(str(fm["description"]).strip())
    p = first_paragraph(body)
    if p:
        parts.append(p)
    hs = headings(body)
    if hs:
        parts.append("Seções: " + "; ".join(hs))
    summary = " ".join(parts)
    summary = re.sub(r"\s+", " ", summary).strip()
    return summary[:MAX_SUMMARY_CHARS]


def build_entry(acervo: Path, path: Path, fm: dict[str, Any], body: str, digest: str) -> tuple[str, list[str], dict[str, str]]:
    rel = path.relative_to(acervo).as_posix()
    micro = microverso_from_path(acervo, path)
    nature = nature_from_path(acervo, path, fm)
    title = str(fm.get("title") or path.stem).strip()
    klass = str(fm.get("class") or "").strip()
    tags = tags_from_frontmatter(fm)
    summary = build_summary(fm, body)
    payload = (
        "AcervoIndex\n"
        f"path: {rel}\n"
        f"microverso: {micro}\n"
        f"nature: {nature}\n"
        f"title: {title}\n"
        f"tags: [{', '.join(tags)}]\n"
        f"class: {klass}\n"
        "status: active\n"
        f"sha256: {digest}\n"
        f"summary: {summary}"
    )
    retain_tags = ["acervo", "AcervoIndex", f"micro:{micro}", f"nature:{nature}"]
    for tag in tags:
        safe = str(tag).strip()
        if safe and safe not in retain_tags:
            retain_tags.append(safe)
    metadata = {
        "path": rel,
        "microverso": micro,
        "nature": nature,
        "sha256": digest,
    }
    return payload, retain_tags, metadata


def iter_markdown(acervo: Path, microverso: str | None, all_scopes: bool, global_scope: bool) -> list[Path]:
    if microverso:
        root = acervo / "micro" / microverso
        if not root.is_dir():
            raise SystemExit(f"Microverso not found: {microverso}")
    elif global_scope:
        root = acervo / "global"
        if not root.is_dir():
            raise SystemExit("Global Acervo layer not found")
    elif all_scopes:
        root = acervo
    else:
        raise SystemExit("Use scan --microverso <slug>, scan --global, or scan --all")
    return sorted(p for p in root.rglob("*.md") if p.is_file())


def make_client(config: dict[str, Any]):
    from hindsight_client import Hindsight

    api_url = os.environ.get("HINDSIGHT_API_URL") or config.get("api_url") or "http://localhost:8888"
    api_key = os.environ.get("HINDSIGHT_API_KEY") or config.get("apiKey") or config.get("api_key")
    timeout = float(os.environ.get("HINDSIGHT_TIMEOUT") or config.get("timeout") or 300)
    return Hindsight(base_url=api_url, api_key=api_key, timeout=timeout)


def load_hindsight_config() -> dict[str, Any]:
    path = Path.home() / ".hermes" / "hindsight" / "config.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def index_one(acervo: Path, path: Path, manifest: dict[str, Any], client: Any, bank_id: str, dry_run: bool) -> tuple[str, str | None]:
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body = split_frontmatter(text)
    skip, reason = should_skip(acervo, path, fm)
    rel = path.relative_to(acervo).as_posix()
    if skip:
        if reason == "deprecated":
            digest = sha256_file(path)
            document_id = "acervo:" + rel
            superseded_by = str(fm.get("superseded_by") or fm.get("deprecated_reason") or "")
            payload = (
                "AcervoIndex\n"
                f"path: {rel}\n"
                f"microverso: {microverso_from_path(acervo, path)}\n"
                f"nature: {nature_from_path(acervo, path, fm)}\n"
                f"title: {fm.get('title') or path.stem}\n"
                "status: deprecated\n"
                f"sha256: {digest}\n"
                f"superseded_by: {superseded_by}"
            )
            if not dry_run:
                client.retain(
                    bank_id=bank_id,
                    content=payload,
                    context="AcervoIndex",
                    document_id=document_id,
                    metadata={"path": rel, "status": "deprecated", "sha256": digest},
                    tags=["acervo", "AcervoIndex", "deprecated"],
                    update_mode="replace",
                    retain_async=False,
                )
            manifest.setdefault("entries", {})[rel] = {
                "sha256": digest,
                "hindsight_document_id": document_id,
                "last_indexed_at": utc_now(),
                "status": "deprecated",
                "microverso": microverso_from_path(acervo, path),
                "nature": nature_from_path(acervo, path, fm),
                "title": str(fm.get("title") or path.stem),
            }
        return "skipped_lifecycle" if reason in {"deprecated", "lifecycle-path"} else "skipped_not_indexable", reason
    digest = sha256_file(path)
    entry = manifest.setdefault("entries", {}).get(rel)
    if entry and entry.get("sha256") == digest and entry.get("status") == "active":
        return "skipped_unchanged", None
    payload, tags, metadata = build_entry(acervo, path, fm, body, digest)
    document_id = "acervo:" + rel
    if not dry_run:
        client.retain(
            bank_id=bank_id,
            content=payload,
            context="AcervoIndex",
            document_id=document_id,
            metadata=metadata,
            tags=tags,
            update_mode="replace",
            retain_async=False,
        )
    manifest.setdefault("entries", {})[rel] = {
        "sha256": digest,
        "hindsight_document_id": document_id,
        "last_indexed_at": utc_now(),
        "status": "active",
        "microverso": metadata["microverso"],
        "nature": metadata["nature"],
        "title": str(fm.get("title") or path.stem),
    }
    return "indexed", None


def cmd_scan(args: argparse.Namespace) -> int:
    acervo = resolve_acervo()
    state_path = acervo / DEFAULT_STATE_REL
    manifest = load_json(state_path, {"version": 1, "indexed_at": None, "entries": {}})
    config = load_hindsight_config()
    bank_id = args.bank_id or os.environ.get("HINDSIGHT_BANK_ID") or config.get("bank_id") or "exocortex"
    client = None if args.dry_run else make_client(config)
    result = IndexResult()
    error_details: list[dict[str, str]] = []
    paths = iter_markdown(acervo, args.microverso, args.all, args.global_scope)
    try:
        for path in paths:
            try:
                status, reason = index_one(acervo, path, manifest, client, bank_id, args.dry_run)
                if status == "indexed":
                    result.indexed += 1
                elif status == "skipped_unchanged":
                    result.skipped_unchanged += 1
                elif status == "skipped_lifecycle":
                    result.skipped_lifecycle += 1
                elif status == "skipped_not_indexable":
                    result.skipped_not_indexable += 1
            except Exception as exc:
                result.errors += 1
                error_details.append({"path": path.relative_to(acervo).as_posix(), "error": str(exc)})
                if args.fail_fast:
                    raise
    finally:
        if client is not None:
            client.close()
    manifest["indexed_at"] = utc_now()
    manifest["last_scan"] = {
        "at": manifest["indexed_at"],
        "scope": args.microverso or "all",
        "dry_run": bool(args.dry_run),
        **result.as_dict(),
        "errors_detail": error_details[:50],
    }
    if not args.dry_run:
        save_json(state_path, manifest)
    print(json.dumps(manifest["last_scan"], indent=2, ensure_ascii=False))
    if error_details:
        print(json.dumps({"errors_detail": error_details}, indent=2, ensure_ascii=False), file=sys.stderr)
    return 1 if result.errors else 0


def cmd_index_file(args: argparse.Namespace) -> int:
    acervo = resolve_acervo()
    path = Path(args.path).expanduser().resolve()
    if not path.is_file():
        raise SystemExit(f"File not found: {path}")
    try:
        path.relative_to(acervo)
    except ValueError:
        raise SystemExit(f"File is outside Acervo: {path}")
    state_path = acervo / DEFAULT_STATE_REL
    manifest = load_json(state_path, {"version": 1, "indexed_at": None, "entries": {}})
    config = load_hindsight_config()
    bank_id = args.bank_id or os.environ.get("HINDSIGHT_BANK_ID") or config.get("bank_id") or "exocortex"
    client = None if args.dry_run else make_client(config)
    try:
        status, reason = index_one(acervo, path, manifest, client, bank_id, args.dry_run)
    finally:
        if client is not None:
            client.close()
    manifest["indexed_at"] = utc_now()
    if not args.dry_run:
        save_json(state_path, manifest)
    print(json.dumps({"path": path.relative_to(acervo).as_posix(), "status": status, "reason": reason, "dry_run": args.dry_run}, indent=2, ensure_ascii=False))
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    acervo = resolve_acervo()
    state_path = acervo / DEFAULT_STATE_REL
    manifest = load_json(state_path, {"version": 1, "indexed_at": None, "entries": {}})
    entries = manifest.get("entries", {})
    active_entries = {rel: meta for rel, meta in entries.items() if meta.get("status") == "active"}
    missing = []
    for rel in active_entries:
        if not (acervo / rel).exists():
            missing.append(rel)
    natures: dict[str, int] = {}
    micros: dict[str, int] = {}
    for meta in active_entries.values():
        natures[meta.get("nature", "unknown")] = natures.get(meta.get("nature", "unknown"), 0) + 1
        micros[meta.get("microverso", "unknown")] = micros.get(meta.get("microverso", "unknown"), 0) + 1
    print(json.dumps({
        "state_path": str(state_path),
        "indexed_at": manifest.get("indexed_at"),
        "entries": len(active_entries),
        "total_manifest_entries": len(entries),
        "by_microverso": dict(sorted(micros.items())),
        "by_nature": dict(sorted(natures.items())),
        "orphaned_manifest_entries": missing[:100],
        "last_scan": manifest.get("last_scan"),
    }, indent=2, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Index Acervo markdown pointers into Hindsight")
    sub = parser.add_subparsers(dest="cmd", required=True)

    scan = sub.add_parser("scan", help="Scan a microverso or all Acervo")
    group = scan.add_mutually_exclusive_group(required=True)
    group.add_argument("--microverso", help="microverso slug, e.g. exocortex-dev")
    group.add_argument("--global", dest="global_scope", action="store_true", help="scan global Acervo layer")
    group.add_argument("--all", action="store_true", help="scan all Acervo")
    scan.add_argument("--bank-id", help="Hindsight bank id override")
    scan.add_argument("--dry-run", action="store_true", help="do not call Hindsight or write state")
    scan.add_argument("--fail-fast", action="store_true", help="abort on first file error")
    scan.set_defaults(func=cmd_scan)

    idx = sub.add_parser("index-file", help="Index one Acervo markdown file")
    idx.add_argument("path")
    idx.add_argument("--bank-id", help="Hindsight bank id override")
    idx.add_argument("--dry-run", action="store_true", help="do not call Hindsight or write state")
    idx.set_defaults(func=cmd_index_file)

    report = sub.add_parser("report", help="Report manifest state")
    report.set_defaults(func=cmd_report)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
