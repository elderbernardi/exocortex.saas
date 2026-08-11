#!/usr/bin/env python3
"""Exact read-before-write lookup for noticias_publicas by canonical URL + cliente_id."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from news_guard import row_key  # noqa: E402
from roster_live_export import (  # noqa: E402
    _DEFAULT_CHUNK_SIZE,
    _DEFAULT_PAGE_SIZE,
    SupabaseRestClient,
    chunked,
    merged_env,
)

SCHEMA = "exocortex/news-lookup-exact/v1"


def load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def candidates_from(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("publish", "candidates", "signals", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    raise ValueError("candidates must be a JSON array or an object with publish[]/candidates[]")


def candidate_keys(candidates: list[dict[str, Any]]) -> set[tuple[str, str | None]]:
    keys: set[tuple[str, str | None]] = set()
    for candidate in candidates:
        url = candidate.get("url_normalized") or candidate.get("url")
        if not url:
            continue
        keys.add(row_key(str(url), candidate.get("cliente_id")))
    return keys


def _in_filter(values: list[str]) -> str:
    escaped = [value.replace('"', '%22') for value in values]
    return "in.(%s)" % ",".join(f'"{value}"' for value in escaped)


def lookup_rows_for_candidates(
    client: Any,
    candidates: list[dict[str, Any]],
    *,
    chunk_size: int = _DEFAULT_CHUNK_SIZE,
) -> list[dict[str, Any]]:
    keys = candidate_keys(candidates)
    if not keys:
        return []

    urls = sorted({url for url, _ in keys})
    found: dict[tuple[str, str | None], dict[str, Any]] = {}
    for url_chunk in chunked(urls, chunk_size):
        rows = client.fetch_rows(
            "noticias_publicas",
            {
                "select": "id,url,cliente_id,ativo,escopo,publicado_em,valido_ate,titulo,headline,fonte,impacto,tipo_fonte",
                "url": _in_filter(url_chunk),
            },
        )
        for row in rows:
            if not isinstance(row, dict) or not row.get("url"):
                continue
            key = row_key(str(row["url"]), row.get("cliente_id"))
            if key in keys:
                found[key] = row
    return [found[key] for key in sorted(found)]


def rows_payload(rows: list[dict[str, Any]], *, auth_mode: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "auth_mode": auth_mode,
        "row_count": len(rows),
        "rows": rows,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", required=True, help="JSON array or object with publish[]/candidates[]")
    parser.add_argument("--output", required=True, help="Path to write the lookup rows payload")
    parser.add_argument("--env-file", help="Optional .env file used when process env is not already populated")
    parser.add_argument("--page-size", type=int, default=_DEFAULT_PAGE_SIZE, help="REST pagination size per request")
    parser.add_argument("--chunk-size", type=int, default=_DEFAULT_CHUNK_SIZE, help="Chunk size for URL in(...) filters")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    env = merged_env(args.env_file)
    client = SupabaseRestClient(env, page_size=args.page_size)
    candidates = candidates_from(load_json(args.candidates))
    rows = lookup_rows_for_candidates(client, candidates, chunk_size=args.chunk_size)
    payload = rows_payload(rows, auth_mode=client.auth_mode.kind)
    Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"auth_mode={client.auth_mode.kind} candidates={len(candidates)} keys={len(candidate_keys(candidates))} rows={len(rows)} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
