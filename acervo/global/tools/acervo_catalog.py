#!/usr/bin/env python3
"""Acervo catalog: derived SQLite index of every canonical object (Plane 2).

catalog.sqlite is a CACHE, never authoritative (04-architecture.md §2).
It is rebuilt from the Markdown frontmatter in Plane 1 and is disposable:
`rm catalog.sqlite && acervoctl reindex` must always work. Nothing may treat
its contents as truth over the files themselves.

Contents:
  objects  — one row per .md object (frontmatter fields + path/hash/mtime)
  links    — typed edges: supersedes / superseded_by / disputed_by /
             relates_to / canonical_from / entity (entities:) / wikilink
  fts      — FTS5 over title/description/body
  meta     — catalog schema_version + built_at (PRAGMA user_version mirrors it)

CLI: build | upsert <file> | query | stats | doctor  (JSON output).
Exposed via `acervoctl reindex` / `acervoctl doctor`.
"""
from __future__ import annotations

import argparse
import json
import os
import posixpath
import re
import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterator

_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

from acervo_hindsight_index import (  # noqa: E402
    SKIP_PARTS,
    microverso_from_path,
    nature_from_path,
    resolve_acervo,
    sha256_file,
    split_frontmatter,
    tags_from_frontmatter,
    utc_now,
)

CATALOG_REL = "global/tools/state/catalog.sqlite"
CATALOG_SCHEMA_VERSION = 1
CATALOG_SKIP = SKIP_PARTS | {"_artifacts"}

STRUCTURED_LINK_KINDS = ("supersedes", "superseded_by", "disputed_by", "relates_to", "canonical_from")
WIKILINK_RE = re.compile(r"\[\[([^\[\]|#\n]+)(?:[|#][^\[\]]*)?\]\]")

# SCHEMA-v0.2.md V2-020: type must match home directory (05-object-model.md §3).
TYPE_DIRS: dict[str, set[str]] = {
    "context": {"context"},
    "knowledge": {"knowledge", "cross-refs"},  # cross-refs are pointer knowledge (06 §6)
    "decision": {"decisions"},
    "episode": {"episodes"},
    "entity": {"entities"},
    "intention": {"intentions"},
    "workflow": {"workflows"},
    "contract": {"contracts"},
    "reflection": {"reflections"},
    "persona": {"persona"},
    "prompt": {"prompts"},
    "template": {"templates"},
    "tool": {"tools"},
    "skill": {"skills"},
    "artifact": {"_artifacts"},
    "conflict": {"knowledge"},  # conflicts live in knowledge/ with type: conflict
}

DDL = """
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);
CREATE TABLE IF NOT EXISTS objects (
    path           TEXT PRIMARY KEY,
    layer          TEXT,
    microverso     TEXT,
    nature         TEXT,
    type           TEXT,
    schema_version TEXT,
    title          TEXT,
    description    TEXT,
    tags           TEXT,
    class          TEXT,
    status         TEXT,
    epistemic      TEXT,
    confidence     TEXT,
    created_at     TEXT,
    observed_at    TEXT,
    valid_from     TEXT,
    valid_until    TEXT,
    review_after   TEXT,
    sensitivity    TEXT,
    sha256         TEXT,
    mtime          REAL
);
CREATE TABLE IF NOT EXISTS links (
    src_path TEXT NOT NULL,
    kind     TEXT NOT NULL,
    target   TEXT NOT NULL,
    UNIQUE(src_path, kind, target)
);
CREATE INDEX IF NOT EXISTS idx_links_src ON links(src_path);
CREATE INDEX IF NOT EXISTS idx_links_target ON links(target);
CREATE INDEX IF NOT EXISTS idx_objects_micro ON objects(microverso);
CREATE INDEX IF NOT EXISTS idx_objects_type ON objects(type);
CREATE VIRTUAL TABLE IF NOT EXISTS fts USING fts5(path UNINDEXED, title, description, body);
"""

OBJECT_COLUMNS = (
    "path", "layer", "microverso", "nature", "type", "schema_version", "title",
    "description", "tags", "class", "status", "epistemic", "confidence",
    "created_at", "observed_at", "valid_from", "valid_until", "review_after",
    "sensitivity", "sha256", "mtime",
)


# ---------------------------------------------------------------- helpers

def resolve_acervo_root(explicit: str | Path | None = None) -> Path:
    if explicit:
        root = Path(explicit).expanduser().resolve()
        if not root.is_dir():
            raise SystemExit(f"Acervo root not found: {root}")
        return root
    return resolve_acervo()


def catalog_path(acervo: Path) -> Path:
    return acervo / CATALOG_REL


def connect(acervo: Path, create: bool = True) -> sqlite3.Connection:
    db = catalog_path(acervo)
    if not create and not db.exists():
        raise SystemExit(f"Catalog not found: {db} (run `build` first)")
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version not in (0, CATALOG_SCHEMA_VERSION):
        # Stale layout from another catalog version: disposable, so recreate.
        conn.executescript(
            "DROP TABLE IF EXISTS fts; DROP TABLE IF EXISTS objects;"
            "DROP TABLE IF EXISTS links; DROP TABLE IF EXISTS meta;"
        )
    conn.executescript(DDL)
    conn.execute(f"PRAGMA user_version = {CATALOG_SCHEMA_VERSION}")
    conn.execute(
        "INSERT OR REPLACE INTO meta(key, value) VALUES ('schema_version', ?)",
        (str(CATALOG_SCHEMA_VERSION),),
    )


def _to_str(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    text = str(value).strip()
    return text or None


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        items = value
    else:
        items = [value]
    out: list[str] = []
    for item in items:
        text = _to_str(item)
        if text:
            out.append(text)
    return out


def effective_status(fm: dict[str, Any]) -> str:
    status = _to_str(fm.get("status"))
    if status:
        return status
    if fm.get("deprecated") is True or str(fm.get("deprecated", "")).lower() == "true":
        return "deprecated"
    if fm.get("quarantined_at"):
        return "quarantined"
    return "active"


def iter_catalog_files(acervo: Path) -> Iterator[Path]:
    """Every canonical .md, skipping lifecycle dirs, _artifacts and _meta logs."""
    for path in sorted(acervo.rglob("*.md")):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(acervo).parts
        if set(rel_parts) & CATALOG_SKIP:
            continue
        if "_meta" in rel_parts and path.name == "log.md":
            continue
        yield path


def extract_links(fm: dict[str, Any], body: str) -> list[tuple[str, str]]:
    links: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()

    def add(kind: str, target: str) -> None:
        key = (kind, target)
        if target and key not in seen:
            seen.add(key)
            links.append(key)

    for kind in STRUCTURED_LINK_KINDS:
        for target in _as_list(fm.get(kind)):
            add(kind, target)
    for slug in _as_list(fm.get("entities")):
        add("entity", slug)
    for match in WIKILINK_RE.finditer(body):
        add("wikilink", match.group(1).strip())
    return links


def parse_object(acervo: Path, path: Path) -> tuple[dict[str, Any], list[tuple[str, str]], str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body = split_frontmatter(text)
    rel = path.relative_to(acervo).as_posix()
    row = {
        "path": rel,
        "layer": rel.split("/", 1)[0],
        "microverso": microverso_from_path(acervo, path),
        "nature": nature_from_path(acervo, path, fm),
        "type": _to_str(fm.get("type")),
        "schema_version": _to_str(fm.get("schema")),
        "title": _to_str(fm.get("title")) or path.stem,
        "description": _to_str(fm.get("description")),
        "tags": json.dumps(tags_from_frontmatter(fm), ensure_ascii=False),
        "class": _to_str(fm.get("class")),
        "status": effective_status(fm),
        "epistemic": _to_str(fm.get("epistemic")),
        "confidence": _to_str(fm.get("confidence")),
        "created_at": _to_str(fm.get("created_at")),
        "observed_at": _to_str(fm.get("observed_at")),
        "valid_from": _to_str(fm.get("valid_from")),
        "valid_until": _to_str(fm.get("valid_until")),
        "review_after": _to_str(fm.get("review_after")),
        "sensitivity": _to_str(fm.get("sensitivity")),
        "sha256": sha256_file(path),
        "mtime": path.stat().st_mtime,
    }
    return row, extract_links(fm, body), body


def _insert_object(conn: sqlite3.Connection, row: dict[str, Any], links: list[tuple[str, str]], body: str) -> None:
    placeholders = ", ".join("?" for _ in OBJECT_COLUMNS)
    cols = ", ".join(f'"{c}"' for c in OBJECT_COLUMNS)
    conn.execute(
        f"INSERT OR REPLACE INTO objects ({cols}) VALUES ({placeholders})",
        tuple(row[c] for c in OBJECT_COLUMNS),
    )
    for kind, target in links:
        conn.execute(
            "INSERT OR IGNORE INTO links(src_path, kind, target) VALUES (?, ?, ?)",
            (row["path"], kind, target),
        )
    conn.execute(
        "INSERT INTO fts(path, title, description, body) VALUES (?, ?, ?, ?)",
        (row["path"], row["title"] or "", row["description"] or "", body),
    )


def _delete_object(conn: sqlite3.Connection, rel: str) -> None:
    conn.execute("DELETE FROM objects WHERE path = ?", (rel,))
    conn.execute("DELETE FROM links WHERE src_path = ?", (rel,))
    conn.execute("DELETE FROM fts WHERE path = ?", (rel,))


# ---------------------------------------------------------------- commands

def build_catalog(acervo: Path) -> dict[str, Any]:
    """Full idempotent rebuild: wipe derived rows, rescan Plane 1."""
    conn = connect(acervo, create=True)
    try:
        ensure_schema(conn)
        with conn:
            conn.execute("DELETE FROM objects")
            conn.execute("DELETE FROM links")
            conn.execute("DELETE FROM fts")
            objects = 0
            links_count = 0
            errors: list[dict[str, str]] = []
            for path in iter_catalog_files(acervo):
                try:
                    row, links, body = parse_object(acervo, path)
                except Exception as exc:  # frontmatter YAML errors etc.
                    errors.append({"path": path.relative_to(acervo).as_posix(), "error": str(exc)})
                    continue
                _insert_object(conn, row, links, body)
                objects += 1
                links_count += len(links)
            conn.execute(
                "INSERT OR REPLACE INTO meta(key, value) VALUES ('built_at', ?)", (utc_now(),)
            )
        return {
            "catalog": str(catalog_path(acervo)),
            "objects": objects,
            "links": links_count,
            "parse_errors": errors,
            "built_at": utc_now(),
        }
    finally:
        conn.close()


def upsert_file(acervo: Path, target: str | Path) -> dict[str, Any]:
    path = Path(target).expanduser().resolve()
    try:
        rel = path.relative_to(acervo).as_posix()
    except ValueError:
        raise SystemExit(f"File is outside Acervo: {path}")
    conn = connect(acervo, create=True)
    try:
        ensure_schema(conn)
        with conn:
            _delete_object(conn, rel)
            if not path.is_file():
                return {"path": rel, "action": "removed"}
            rel_parts = path.relative_to(acervo).parts
            if set(rel_parts) & CATALOG_SKIP or ("_meta" in rel_parts and path.name == "log.md"):
                return {"path": rel, "action": "skipped", "reason": "lifecycle-path"}
            row, links, body = parse_object(acervo, path)
            _insert_object(conn, row, links, body)
            return {"path": rel, "action": "upserted", "links": len(links)}
    finally:
        conn.close()


def query_catalog(
    acervo: Path,
    type_: str | None = None,
    microverso: str | None = None,
    status: str | None = None,
    layer: str | None = None,
    fts: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    conn = connect(acervo, create=False)
    try:
        where: list[str] = []
        params: list[Any] = []
        for column, value in (("type", type_), ("microverso", microverso), ("status", status), ("layer", layer)):
            if value:
                where.append(f'o."{column}" = ?')
                params.append(value)
        if fts:
            sql = "SELECT o.* FROM fts JOIN objects o ON o.path = fts.path WHERE fts MATCH ?"
            params.insert(0, fts)
            if where:
                sql += " AND " + " AND ".join(where)
            sql += " ORDER BY rank LIMIT ?"
        else:
            sql = "SELECT o.* FROM objects o"
            if where:
                sql += " WHERE " + " AND ".join(where)
            sql += " ORDER BY o.path LIMIT ?"
        params.append(limit)
        rows = []
        for row in conn.execute(sql, params).fetchall():
            item = dict(row)
            item["tags"] = json.loads(item.get("tags") or "[]")
            rows.append(item)
        return rows
    finally:
        conn.close()


def stats_catalog(acervo: Path) -> dict[str, Any]:
    conn = connect(acervo, create=False)
    try:
        def group(column: str) -> dict[str, int]:
            sql = f'SELECT COALESCE("{column}", \'(none)\') AS k, COUNT(*) AS n FROM objects GROUP BY k ORDER BY k'
            return {row["k"]: row["n"] for row in conn.execute(sql).fetchall()}

        meta = {row["key"]: row["value"] for row in conn.execute("SELECT key, value FROM meta").fetchall()}
        return {
            "catalog": str(catalog_path(acervo)),
            "built_at": meta.get("built_at"),
            "catalog_schema_version": meta.get("schema_version"),
            "objects": conn.execute("SELECT COUNT(*) FROM objects").fetchone()[0],
            "links": conn.execute("SELECT COUNT(*) FROM links").fetchone()[0],
            "by_layer": group("layer"),
            "by_type": group("type"),
            "by_status": group("status"),
            "by_microverso": group("microverso"),
        }
    finally:
        conn.close()


# ---------------------------------------------------------------- doctor

def _dir_nature(rel: str) -> str:
    parts = rel.split("/")
    if len(parts) >= 4 and parts[0] == "micro":
        return parts[2]
    if len(parts) >= 3 and parts[0] in {"global", "shared"}:
        return parts[1]
    return ""


def _target_candidates(src_rel: str, target: str) -> list[str]:
    t = target.strip().strip('"').strip("'")
    cands = []
    for base in ([t, t + ".md"] if not t.endswith(".md") else [t]):
        cands.append(base)
        if base.startswith("acervo/"):
            cands.append(base[len("acervo/"):])
        cands.append(posixpath.normpath(posixpath.join(posixpath.dirname(src_rel), base)))
    return cands


def doctor(acervo: Path) -> dict[str, Any]:
    """Health report: broken links, lifecycle coherence (v0.2), type↔dir,
    catalog-vs-disk drift, duplicate titles. ok == no ERROR findings.

    Severity policy: structured-link breaks and v0.2 rule violations are
    ERROR; broken wikilinks (associative, lazily-created targets — P9),
    drift (remedy: reindex) and duplicate titles are WARN.
    """
    db = catalog_path(acervo)
    if not db.exists():
        raise SystemExit(f"Catalog not found: {db} (run `build`/`acervoctl reindex` first)")
    conn = connect(acervo, create=False)
    findings: list[dict[str, str]] = []

    def report(severity: str, check: str, path: str, message: str) -> None:
        findings.append({"severity": severity, "check": check, "path": path, "message": message})

    try:
        objects = {row["path"]: dict(row) for row in conn.execute("SELECT * FROM objects").fetchall()}
        links = [dict(row) for row in conn.execute("SELECT src_path, kind, target FROM links").fetchall()]

        # --- catalog-vs-disk drift ---
        disk: dict[str, Path] = {p.relative_to(acervo).as_posix(): p for p in iter_catalog_files(acervo)}
        for rel, row in objects.items():
            path = disk.get(rel)
            if path is None:
                report("WARN", "drift-missing", rel, "in catalog but missing on disk (reindex)")
            elif abs(path.stat().st_mtime - (row["mtime"] or 0)) > 1e-6 and sha256_file(path) != row["sha256"]:
                report("WARN", "drift-changed", rel, "file changed since catalog build (reindex)")
        for rel in sorted(set(disk) - set(objects)):
            report("WARN", "drift-extra", rel, "on disk but not in catalog (reindex)")

        stems: dict[str, str] = {}
        titles: dict[str, str] = {}
        for rel in disk:
            stems.setdefault(Path(rel).stem.lower(), rel)
        for rel, row in objects.items():
            if row.get("title"):
                titles.setdefault(str(row["title"]).strip().lower(), rel)

        def resolve(src_rel: str, target: str) -> str | None:
            for cand in _target_candidates(src_rel, target):
                if cand in disk:
                    return cand
            key = target.strip().strip('"').strip("'").lower()
            if key.endswith(".md"):
                key = key[:-3]
            return stems.get(key) or titles.get(key)

        # --- broken links (V2-031 existence half + wikilinks) ---
        supersedes_map: list[tuple[str, str, str | None]] = []
        superseded_by_links: dict[str, list[str]] = {}
        for link in links:
            src, kind, target = link["src_path"], link["kind"], link["target"]
            if kind == "entity":
                continue  # entity registry lands in Phase 2
            resolved = resolve(src, target)
            if kind == "wikilink":
                if resolved is None:
                    report("WARN", "broken-wikilink", src, f"[[{target}]] has no matching file/title")
                continue
            if resolved is None:
                # canonical_from records historical provenance (the origin may be
                # legitimately retired) — advisory, not an operational defect.
                sev = "WARN" if kind == "canonical_from" else "ERROR"
                report(sev, "broken-link", src, f"{kind} target not found on disk: {target}")
            if kind == "supersedes":
                supersedes_map.append((src, target, resolved))
            if kind == "superseded_by":
                superseded_by_links.setdefault(src, []).append(target)

        # --- v0.2-only lifecycle rules ---
        for rel, row in objects.items():
            if row.get("schema_version") != "acervo/v0.2":
                continue
            # V2-030: superseded status <=> superseded_by
            if row.get("status") == "superseded" and rel not in superseded_by_links:
                report("ERROR", "V2-030", rel, "status: superseded without superseded_by")
            if rel in superseded_by_links and row.get("status") != "superseded":
                report("ERROR", "V2-030", rel, f"superseded_by present but status: {row.get('status')}")
            # V2-020: type <-> directory match (_meta is infra: exempt, matching
            # the validator's exemption; `conflict` may live in knowledge/)
            obj_type = row.get("type")
            dir_nature = _dir_nature(rel)
            expected = TYPE_DIRS.get(obj_type or "")
            if dir_nature == "_meta" or obj_type == "conflict":
                pass
            elif obj_type and dir_nature and expected and dir_nature not in expected:
                report("ERROR", "V2-020", rel, f"type: {obj_type} does not match directory {dir_nature}/")

        # V2-031 status half: supersedes target must be status: superseded
        for src, target, resolved in supersedes_map:
            if objects.get(src, {}).get("schema_version") != "acervo/v0.2":
                continue
            target_row = objects.get(resolved) if resolved else None
            if target_row and target_row.get("status") != "superseded":
                report("ERROR", "V2-031", src, f"supersedes {resolved} which is status: {target_row.get('status')}")

        # --- duplicate titles within same microverso (WARN) ---
        dup_sql = (
            "SELECT microverso, LOWER(title) AS t, GROUP_CONCAT(path, ', ') AS paths, COUNT(*) AS n "
            "FROM objects WHERE title IS NOT NULL AND title != '' "
            "GROUP BY microverso, t HAVING n > 1"
        )
        for row in conn.execute(dup_sql).fetchall():
            report("WARN", "duplicate-title", row["paths"], f"duplicate title '{row['t']}' in microverso {row['microverso']}")

        errors = sum(1 for f in findings if f["severity"] == "ERROR")
        warnings = sum(1 for f in findings if f["severity"] == "WARN")
        return {
            "ok": errors == 0,
            "checked_objects": len(objects),
            "checked_links": len(links),
            "errors": errors,
            "warnings": warnings,
            "findings": findings,
        }
    finally:
        conn.close()


# ---------------------------------------------------------------- CLI

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Derived catalog.sqlite for the Acervo (Plane 2, disposable)")
    parser.add_argument("--acervo", help="Acervo root (default: $ACERVO or standard fallbacks)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("build", help="Full rebuild of catalog.sqlite")

    upsert = sub.add_parser("upsert", help="Incrementally (re)index one file")
    upsert.add_argument("file")

    query = sub.add_parser("query", help="Filtered metadata query (JSON)")
    query.add_argument("--type", dest="type_")
    query.add_argument("--microverso")
    query.add_argument("--status")
    query.add_argument("--layer")
    query.add_argument("--fts", help="FTS5 MATCH expression over title/description/body")
    query.add_argument("--limit", type=int, default=100)

    sub.add_parser("stats", help="Counts by layer/type/status/microverso")
    sub.add_parser("doctor", help="Integrity report (exit 1 on ERROR findings)")

    args = parser.parse_args(argv)
    acervo = resolve_acervo_root(args.acervo)

    if args.cmd == "build":
        payload: Any = build_catalog(acervo)
    elif args.cmd == "upsert":
        payload = upsert_file(acervo, args.file)
    elif args.cmd == "query":
        payload = query_catalog(
            acervo, type_=args.type_, microverso=args.microverso, status=args.status,
            layer=args.layer, fts=args.fts, limit=args.limit,
        )
    elif args.cmd == "stats":
        payload = stats_catalog(acervo)
    else:  # doctor
        payload = doctor(acervo)

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.cmd == "doctor" and not payload["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
