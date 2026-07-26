#!/usr/bin/env python3
"""Disposable Acervo adapter for the public benchmark JSON protocol.

One request is read from stdin and one response is written to stdout.  Every
case gets a fresh temporary Acervo, so fictional benchmark memories cannot
contaminate either another case or the user's live Acervo.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
TOOLS = REPO / "acervo" / "global" / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from acervo_catalog import build_catalog  # noqa: E402
from acervo_hindsight_index import split_frontmatter  # noqa: E402
from acervo_retrieve import Retriever  # noqa: E402


def slug(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def render_session(session: dict[str, Any], index: int) -> str:
    title = f"Benchmark conversation session {index:04d}"
    date = session.get("date") or ""
    body = [f"# {title}", "", f"Session date: {date}", ""]
    for turn in session.get("turns", []):
        body += [f"## {turn.get('role', 'unknown')}", "", str(turn.get("content", "")), ""]
    frontmatter = [
        "---", "schema_version: '0.2'", "type: episode", f"title: {json.dumps(title)}",
        f"description: {json.dumps('Imported public benchmark conversation session')}",
        f"status: {session.get('status', 'active')}", "class: volatil",
        f"sensitivity: {session.get('sensitivity', 'internal')}", "tags: [public-benchmark]",
        f"observed_at: {json.dumps(str(date))}", "---", "",
    ]
    return "\n".join(frontmatter + body)


def make_acervo(root: Path, request: dict[str, Any], flat: bool) -> dict[str, str]:
    micro = f"lme-{slug(str(request['case_id']))}"
    (root / "global" / "tools" / "state").mkdir(parents=True, exist_ok=True)
    mapping: dict[str, str] = {}
    for index, session in enumerate(request.get("sessions", []), 1):
        session_micro = str(session.get("microverse") or micro)
        home = root / "shared" / "episodes" if flat else root / "micro" / session_micro / "episodes"
        home.mkdir(parents=True, exist_ok=True)
        path = home / f"session-{index:04d}-{slug(str(session['session_id']))}.md"
        path.write_text(render_session(session, index), encoding="utf-8")
        mapping[path.relative_to(root).as_posix()] = str(session["session_id"])
    return mapping


def run_consolidator(command: str, root: Path, request: dict[str, Any], timeout: int) -> None:
    env = {
        **os.environ,
        "ACERVO_ROOT": str(root),
        "ACTIVE_MICROVERSO": f"lme-{slug(str(request['case_id']))}",
        "ACERVO_BENCHMARK_CASE_ID": str(request["case_id"]),
    }
    proc = subprocess.run(
        shlex.split(command), input=json.dumps(request, ensure_ascii=False), text=True,
        capture_output=True, timeout=timeout, env=env,
    )
    if proc.returncode:
        raise RuntimeError(f"consolidator exited {proc.returncode}: {proc.stderr[-2000:]}")


def provenance_for_path(root: Path, relative: str, raw_mapping: dict[str, str]) -> list[str]:
    if relative in raw_mapping:
        return [raw_mapping[relative]]
    path = root / relative
    if not path.is_file():
        return []
    frontmatter, _body = split_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
    value = frontmatter.get("benchmark_session_ids", [])
    if isinstance(value, str):
        value = [value]
    return [str(x) for x in value] if isinstance(value, list) else []


def object_type_for_path(root: Path, relative: str) -> str | None:
    path = root / relative
    if not path.is_file():
        return None
    frontmatter, _body = split_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
    value = frontmatter.get("type")
    return str(value) if value else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--consolidator-command")
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--keep-root", type=Path, help="debug only: use and preserve this disposable root")
    args = parser.parse_args(argv)
    request = json.load(sys.stdin)
    condition = request.get("condition")
    if condition not in {"full", "no-consolidation", "catalog-only", "flat-no-microverse"}:
        raise SystemExit(f"unsupported Acervo condition: {condition}")
    if condition == "full" and not args.consolidator_command:
        raise SystemExit("full requires --consolidator-command")

    temporary = None
    if args.keep_root:
        root = args.keep_root.resolve()
        root.mkdir(parents=True, exist_ok=True)
    else:
        temporary = tempfile.TemporaryDirectory(prefix="acervo-public-bench-")
        root = Path(temporary.name)
    started = time.perf_counter()
    try:
        mapping = make_acervo(root, request, flat=condition == "flat-no-microverse")
        if condition == "full":
            run_consolidator(args.consolidator_command, root, request, args.timeout)
        build_catalog(root)
        scope = "global" if condition == "flat-no-microverse" else str(request.get("scope") or f"lme-{slug(str(request['case_id']))}")
        result = Retriever(root).retrieve(
            str(request["question"]), scope=scope, k=int(request.get("top_k", 5)),
            allow_scopes=[str(x) for x in request.get("allow_scopes", [])],
        )
        paths = [item["path"] for item in result.get("items", [])]
        session_ids = []
        for path in paths:
            for session_id in provenance_for_path(root, path, mapping):
                if session_id not in session_ids:
                    session_ids.append(session_id)
        sessions_by_id = {str(s["session_id"]): s for s in request.get("sessions", [])}
        contexts = []
        for path in paths:
            source_ids = provenance_for_path(root, path, mapping)
            if path in mapping and mapping[path] in sessions_by_id:
                contexts.append(sessions_by_id[mapping[path]])
            else:
                contexts.append({
                    "path": path,
                    "source_session_ids": source_ids,
                    "content": (root / path).read_text(encoding="utf-8", errors="replace") if (root / path).is_file() else "",
                })
        response = {
            "retrieved_session_ids": session_ids,
            "contexts": contexts,
            "retrieved_paths": paths,
            "found": bool(result.get("found")),
            "route": result.get("route"),
            "extracted_object_types": sorted({
                object_type
                for path in paths
                if (object_type := object_type_for_path(root, path)) is not None
            }),
            "latency_ms": (time.perf_counter() - started) * 1000,
            "adapter_root_policy": "preserved" if args.keep_root else "deleted-after-response",
        }
        print(json.dumps(response, ensure_ascii=False))
        return 0
    finally:
        if temporary is not None:
            temporary.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
