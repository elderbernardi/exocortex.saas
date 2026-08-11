#!/usr/bin/env python3
"""Deterministic signal→client matching and pre-LLM preparation for micro news."""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_dossier import (  # noqa: E402
    collapse_ws,
    ensure_list,
    make_signal,
    normalize_agent_reach_items,
    normalize_crawler_items,
    normalize_title,
    parse_any_date,
)
from news_guard import partition, row_key  # noqa: E402
from lookup_noticias_exact import lookup_rows_for_candidates, rows_payload  # noqa: E402

SCHEMA = "exocortex/micro-news-match/v1"
MIN_ALIAS_LENGTH = 4
EXACT_THRESHOLD = 60
PROBABLE_THRESHOLD = 40


def normalize_text(value: str | None) -> str:
    raw = collapse_ws(value or "")
    if not raw:
        return ""
    raw = unicodedata.normalize("NFKD", raw)
    raw = raw.encode("ascii", "ignore").decode("ascii")
    raw = re.sub(r"[^a-z0-9]+", " ", raw.casefold())
    return collapse_ws(raw)


def load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def signal_text(signal: dict[str, Any]) -> str:
    pieces = [
        signal.get("title"),
        signal.get("snippet"),
    ]
    metadata = signal.get("metadata")
    if isinstance(metadata, dict):
        pieces.extend(str(value) for value in metadata.values() if value is not None)
    return normalize_text(" ".join(str(piece or "") for piece in pieces))


def contains_alias(text: str, alias: str) -> bool:
    haystack = f" {text} "
    needle = f" {alias} "
    return needle in haystack


def title_starts_with_brand(title: str, alias: str) -> bool:
    if title == alias or title.startswith(f"{alias} "):
        return True
    for prefix in ("rede", "grupo", "supermercado", "comercial", "atacado", "mercado"):
        prefixed = f"{prefix} {alias}"
        if title == prefixed or title.startswith(f"{prefixed} "):
            return True
    return False


def load_signals(path: str) -> list[dict[str, Any]]:
    payload = load_json(path)
    if isinstance(payload, list) and payload and isinstance(payload[0], dict) and payload[0].get("url_normalized"):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict) and isinstance(payload.get("signals"), list):
        return [item for item in payload["signals"] if isinstance(item, dict)]

    signals: list[dict[str, Any]] = []
    signals.extend(normalize_crawler_items(payload))
    signals.extend(normalize_agent_reach_items(payload))
    if signals:
        return signals

    for item in ensure_list(payload):
        if not isinstance(item, dict):
            continue
        normalized = make_signal(
            title=str(item.get("title", "")),
            url=str(item.get("url") or item.get("link") or ""),
            published_at=str(item.get("published_at") or item.get("date") or item.get("publicado_em") or ""),
            source=str(item.get("source") or item.get("site") or item.get("domain") or "desconhecido"),
            snippet=str(item.get("snippet") or item.get("summary") or ""),
            channel=str(item.get("channel") or "open"),
            evidence_kind=str(item.get("evidence_kind") or "news"),
            metadata=item.get("metadata") if isinstance(item.get("metadata"), dict) else {},
        )
        if normalized:
            signals.append(normalized)
    return signals


def load_manifest_clients(index_path: str) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    index = load_json(index_path)
    root = Path(index_path).resolve().parent
    all_clients: list[dict[str, Any]] = []
    by_seller: dict[str, list[dict[str, Any]]] = {}
    by_client: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for seller_entry in index.get("sellers", []):
        seller_id = seller_entry.get("seller_id")
        json_path = seller_entry.get("json_path")
        if not seller_id or not json_path:
            continue
        manifest = load_json(str(root / json_path))
        clients: list[dict[str, Any]] = []
        seller_info = manifest.get("seller") or {}
        for client in manifest.get("clients", []):
            if not isinstance(client, dict):
                continue
            enriched = dict(client)
            enriched["seller_id"] = seller_id
            enriched["seller_name"] = seller_info.get("seller_name")
            enriched["seller_email"] = seller_info.get("seller_email")
            clients.append(enriched)
            all_clients.append(enriched)
            by_client[str(client.get("cliente_id"))].append(enriched)
        by_seller[str(seller_id)] = clients
    return all_clients, by_seller, dict(by_client)


def score_client_match(signal: dict[str, Any], client: dict[str, Any]) -> tuple[int, list[str]]:
    text = signal_text(signal)
    title_text = normalize_text(signal.get("title"))
    reasons: list[str] = []
    score = 0
    aliases = [normalize_text(alias) for alias in client.get("aliases") or []]
    aliases = [alias for alias in aliases if alias]
    brand_aliases = [normalize_text(alias) for alias in client.get("brand_aliases") or []]
    brand_aliases = [alias for alias in brand_aliases if alias]

    for alias in aliases:
        if alias.isdigit() and contains_alias(text, alias):
            score = max(score, 90)
            reasons.append(f"cnpj:{alias}")
            break

    for alias in brand_aliases:
        if len(alias) < MIN_ALIAS_LENGTH:
            continue
        if title_starts_with_brand(title_text, alias):
            score = max(score, EXACT_THRESHOLD)
            reasons.append(f"brand_title_prefix:{alias}")
            break

    for alias in aliases:
        if alias.isdigit() or len(alias) < MIN_ALIAS_LENGTH:
            continue
        if contains_alias(text, alias):
            score += 50 if alias == normalize_text(client.get("nome_fantasia")) else 35
            reasons.append(f"alias:{alias}")
            break

    city = normalize_text(client.get("cidade"))
    uf = normalize_text(client.get("uf"))
    if city and uf and f"{city} {uf}" in text:
        score += 15
        reasons.append(f"praca:{city}-{uf}")
    elif city and city in text:
        score += 8
        reasons.append(f"cidade:{city}")

    title_normalized = signal.get("title_normalized") or normalize_title(str(signal.get("title") or ""))
    fantasy = normalize_text(client.get("nome_fantasia"))
    if fantasy and fantasy == title_normalized:
        score = max(score, 85)
        reasons.append("titulo_exato_fantasia")

    return score, reasons


def match_signals(signals: list[dict[str, Any]], clients: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    buckets: dict[str, list[dict[str, Any]]] = {
        "matched_exact": [],
        "matched_probable": [],
        "unmatched": [],
        "discarded_noise": [],
    }
    for signal in signals:
        if not signal.get("url_normalized") or not signal.get("title"):
            buckets["discarded_noise"].append({"signal": signal, "reason": "missing_url_or_title"})
            continue

        scored: list[dict[str, Any]] = []
        for client in clients:
            score, reasons = score_client_match(signal, client)
            if score <= 0:
                continue
            scored.append(
                {
                    "signal": signal,
                    "cliente_id": client.get("cliente_id"),
                    "seller_id": client.get("seller_id"),
                    "seller_name": client.get("seller_name"),
                    "seller_email": client.get("seller_email"),
                    "client": client,
                    "match_score": score,
                    "match_reasons": reasons,
                }
            )
        scored.sort(key=lambda item: item["match_score"], reverse=True)

        if not scored:
            buckets["unmatched"].append({"signal": signal})
            continue

        top = scored[0]
        if top["match_score"] >= EXACT_THRESHOLD:
            buckets["matched_exact"].append(top)
            continue
        if top["match_score"] >= PROBABLE_THRESHOLD:
            top = dict(top)
            top["alternatives"] = scored[1:4]
            buckets["matched_probable"].append(top)
            continue
        buckets["unmatched"].append({"signal": signal, "best_candidate": top})
    return buckets


def dedupe_exact_matches(matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best_by_key: dict[tuple[str, str | None], dict[str, Any]] = {}
    for match in matches:
        candidate = build_publish_candidate(match)
        key = row_key(candidate["url_normalized"], candidate.get("cliente_id"))
        previous = best_by_key.get(key)
        if previous is None or match["match_score"] > previous["match_score"]:
            best_by_key[key] = {**match, "candidate": candidate}
    return list(best_by_key.values())


def build_publish_candidate(match: dict[str, Any]) -> dict[str, Any]:
    signal = match["signal"]
    client = match["client"]
    return {
        "schema": SCHEMA,
        "cliente_id": client.get("cliente_id"),
        "seller_id": client.get("seller_id"),
        "seller_name": client.get("seller_name"),
        "title": signal.get("title"),
        "headline": signal.get("title"),
        "url": signal.get("url"),
        "url_normalized": signal.get("url_normalized"),
        "fonte": signal.get("source"),
        "publicado_em": signal.get("published_at") or parse_any_date(str(signal.get("published_at") or "")),
        "snippet": signal.get("snippet"),
        "channel": signal.get("channel"),
        "evidence_kind": signal.get("evidence_kind"),
        "match_score": match.get("match_score"),
        "match_reasons": match.get("match_reasons") or [],
        "client_name": client.get("nome_fantasia") or client.get("nome"),
        "city": client.get("cidade"),
        "uf": client.get("uf"),
        "access_types": client.get("access_types") or [],
        "client_context": {
            "cliente_id": client.get("cliente_id"),
            "nome": client.get("nome"),
            "nome_fantasia": client.get("nome_fantasia"),
            "cidade": client.get("cidade"),
            "uf": client.get("uf"),
            "tabela_atual": client.get("tabela_atual"),
            "rfm_label": client.get("rfm_label"),
            "access_types": client.get("access_types") or [],
            "brand_aliases": client.get("brand_aliases") or [],
        },
    }


def load_existing_rows(path: str | None) -> list[dict[str, Any]]:
    if not path:
        return []
    payload = load_json(path)
    rows = ensure_list(payload)
    return [row for row in rows if isinstance(row, dict)]


def existing_rows_by_key(rows: list[dict[str, Any]]) -> dict[tuple[str, str | None], dict[str, Any]]:
    existing: dict[tuple[str, str | None], dict[str, Any]] = {}
    for row in rows:
        url = row.get("url_normalized") or row.get("url")
        if not url:
            continue
        existing[row_key(str(url), row.get("cliente_id"))] = {
            "id": row.get("id"),
            "ativo": row.get("ativo"),
        }
    return existing


def resolve_existing_rows(
    *,
    existing_path: str | None,
    lookup_env_file: str | None,
    lookup_output: str | None,
    publish_candidates: list[dict[str, Any]],
    lookup_page_size: int = 500,
    lookup_chunk_size: int = 75,
) -> tuple[list[dict[str, Any]], str]:
    if existing_path:
        return load_existing_rows(existing_path), "file"
    if not lookup_env_file:
        return [], "none"

    from roster_live_export import SupabaseRestClient, merged_env  # noqa: WPS433

    env = merged_env(lookup_env_file)
    client = SupabaseRestClient(env, page_size=lookup_page_size)
    rows = lookup_rows_for_candidates(client, publish_candidates, chunk_size=lookup_chunk_size)
    if lookup_output:
        payload = rows_payload(rows, auth_mode=client.auth_mode.kind)
        write_json(Path(lookup_output), payload)
    return rows, f"live:{client.auth_mode.kind}"


def group_matches_by_seller(matches: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for match in matches:
        grouped[str(match.get("seller_id"))].append(match)
    return dict(grouped)


def group_matches_by_client(matches: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for match in matches:
        grouped[str(match.get("cliente_id"))].append(match)
    return dict(grouped)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--signals", required=True, help="Input JSON with open signals or normalized signals[]")
    parser.add_argument("--manifests-index", required=True, help="Path to manifests/index.json produced by roster_freeze")
    parser.add_argument("--out-dir", required=True, help="Output directory for matched/ and prepared/ artifacts")
    parser.add_argument("--existing", help="Optional JSON with existing noticias_publicas rows (active and/or retired)")
    parser.add_argument("--lookup-env-file", help="Optional .env file to execute exact live lookup when --existing is not provided")
    parser.add_argument("--lookup-output", help="Optional path to persist rows returned by live lookup")
    parser.add_argument("--lookup-page-size", type=int, default=500, help="REST pagination size for live lookup")
    parser.add_argument("--lookup-chunk-size", type=int, default=75, help="Chunk size for live lookup URL filters")
    parser.add_argument("--max-age-days", type=int, default=10, help="Freshness cutoff by publicado_em")
    parser.add_argument("--today", help="Optional YYYY-MM-DD override for stale calculation")
    args = parser.parse_args(argv)

    signals = load_signals(args.signals)
    clients, _, _ = load_manifest_clients(args.manifests_index)
    buckets = match_signals(signals, clients)

    exact_matches = dedupe_exact_matches(buckets["matched_exact"])
    publish_candidates = [item["candidate"] for item in exact_matches]
    existing_rows, existing_source = resolve_existing_rows(
        existing_path=args.existing,
        lookup_env_file=args.lookup_env_file,
        lookup_output=args.lookup_output,
        publish_candidates=publish_candidates,
        lookup_page_size=args.lookup_page_size,
        lookup_chunk_size=args.lookup_chunk_size,
    )
    prepared = partition(
        publish_candidates,
        existing_rows_by_key(existing_rows),
        max_age_days=args.max_age_days,
        today=args.today or date.today().isoformat(),
    )

    skipped = {
        "already_active": prepared["skip_active"],
        "retired": prepared["skip_retired"],
        "stale": prepared["skip_stale"],
        "needs_review": [build_publish_candidate(item) for item in buckets["matched_probable"]],
        "unmatched": buckets["unmatched"],
        "discarded_noise": buckets["discarded_noise"],
    }

    out_root = Path(args.out_dir)
    write_json(out_root / "matched" / "per_seller" / "index.json", group_matches_by_seller([item["candidate"] for item in exact_matches]))
    write_json(out_root / "matched" / "per_client" / "index.json", group_matches_by_client([item["candidate"] for item in exact_matches]))
    write_json(out_root / "matched" / "unmatched.json", buckets["unmatched"])
    write_json(out_root / "prepared" / "pre_llm_publishable.json", prepared["publish"])
    write_json(out_root / "prepared" / "skipped.json", skipped)

    summary = {
        "schema": SCHEMA,
        "signals": len(signals),
        "clients": len(clients),
        "matched_exact": len(buckets["matched_exact"]),
        "matched_probable": len(buckets["matched_probable"]),
        "publishable": len(prepared["publish"]),
        "skip_active": len(prepared["skip_active"]),
        "skip_retired": len(prepared["skip_retired"]),
        "skip_stale": len(prepared["skip_stale"]),
        "needs_review": len(skipped["needs_review"]),
        "unmatched": len(buckets["unmatched"]),
        "discarded_noise": len(buckets["discarded_noise"]),
        "existing_rows": len(existing_rows),
        "existing_source": existing_source,
        "out_dir": args.out_dir,
    }
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
