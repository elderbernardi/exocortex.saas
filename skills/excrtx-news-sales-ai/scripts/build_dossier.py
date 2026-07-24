#!/usr/bin/env python3
"""Build a Route B news dossier for Sales-AI publication workflows.

This script is deterministic on purpose. It does not call LLMs, MCP servers, or
remote APIs. It normalizes previously collected source payloads into a machine-
readable dossier that a Hermes/Exocortex agent can curate and publish.

Usage:
    python3 skills/excrtx-news-sales-ai/scripts/build_dossier.py \
      --job-context /tmp/news-context.json \
      --crawler /tmp/crawler.json \
      --agent-reach /tmp/agent-reach.json \
      --docbrain /tmp/docbrain.json \
      --output pretty
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse

SCHEMA = "exocortex/news-route-b-dossier/v1"
DEFAULT_MAX_SIGNALS = 40
TRACKING_KEYS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "utm_id",
    "gclid",
    "fbclid",
    "mc_cid",
    "mc_eid",
    "ref",
    "ref_src",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(payload: Any, path: str | Path | None, pretty: bool = False) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2 if pretty else None)
    if path:
        Path(path).write_text(text + ("\n" if pretty else ""), encoding="utf-8")
    else:
        sys.stdout.write(text)
        if pretty:
            sys.stdout.write("\n")


def collapse_ws(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def normalize_title(value: str) -> str:
    value = collapse_ws(value).lower()
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return collapse_ws(value)


def normalize_url(value: str) -> str:
    raw = collapse_ws(value)
    if not raw:
        return ""
    parsed = urlparse(raw)
    query_pairs: list[tuple[str, str]] = []
    if parsed.query:
        for pair in parsed.query.split("&"):
            if not pair:
                continue
            if "=" in pair:
                key, val = pair.split("=", 1)
            else:
                key, val = pair, ""
            if key.lower() not in TRACKING_KEYS:
                query_pairs.append((key, val))
    query = "&".join(
        f"{key}={val}" if val else key
        for key, val in sorted(query_pairs, key=lambda item: item[0].lower())
    )
    path = re.sub(r"/+", "/", parsed.path or "/")
    if path != "/":
        path = path.rstrip("/")
    normalized = parsed._replace(
        scheme=(parsed.scheme or "https").lower(),
        netloc=parsed.netloc.lower(),
        path=path or "/",
        params="",
        query=query,
        fragment="",
    )
    return urlunparse(normalized)


def parse_any_date(value: str | None) -> str:
    raw = collapse_ws(value or "")
    if not raw:
        return ""
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        return raw
    for candidate in (
        raw.replace("Z", "+00:00"),
        raw,
    ):
        try:
            dt = datetime.fromisoformat(candidate)
            return dt.date().isoformat()
        except ValueError:
            pass
    return raw[:10] if len(raw) >= 10 else raw


def ensure_list(payload: Any) -> list[Any]:
    if payload is None:
        return []
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("items", "results", "data", "signals", "entries"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    return []


def make_signal(
    *,
    title: str,
    url: str,
    published_at: str,
    source: str,
    snippet: str,
    channel: str,
    evidence_kind: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    title = collapse_ws(title)
    url_normalized = normalize_url(url)
    source = collapse_ws(source)
    snippet = collapse_ws(snippet)
    published_at = parse_any_date(published_at)
    if not title or not url_normalized or not source:
        return None
    return {
        "title": title,
        "title_normalized": normalize_title(title),
        "url": collapse_ws(url),
        "url_normalized": url_normalized,
        "published_at": published_at,
        "source": source,
        "snippet": snippet,
        "channel": channel,
        "evidence_kind": evidence_kind,
        "metadata": metadata or {},
    }


def normalize_crawler_items(payload: Any) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for item in ensure_list(payload):
        if not isinstance(item, dict):
            continue
        normalized = make_signal(
            title=str(item.get("title", "")),
            url=str(item.get("url", "")),
            published_at=str(item.get("date") or item.get("published_at") or ""),
            source=str(item.get("source", "crawler-brasil")),
            snippet=str(item.get("snippet", "")),
            channel="crawler-brasil",
            evidence_kind="news",
            metadata={
                "domain": item.get("domain"),
                "retrieved_at": item.get("retrieved_at"),
            },
        )
        if normalized:
            items.append(normalized)
    return items


def normalize_agent_reach_items(payload: Any) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for item in ensure_list(payload):
        if not isinstance(item, dict):
            continue
        source = (
            item.get("source")
            or item.get("source_name")
            or item.get("site")
            or item.get("domain")
            or item.get("channel")
            or "agent-reach"
        )
        snippet = item.get("snippet") or item.get("summary") or item.get("excerpt") or item.get("content", "")
        normalized = make_signal(
            title=str(item.get("title", "")),
            url=str(item.get("url") or item.get("link") or ""),
            published_at=str(item.get("published_at") or item.get("date") or item.get("retrieved_at") or ""),
            source=str(source),
            snippet=str(snippet),
            channel=str(item.get("channel") or "agent-reach"),
            evidence_kind="news",
            metadata={
                "author": item.get("author"),
                "score": item.get("score"),
                "source_type": item.get("source_type"),
            },
        )
        if normalized:
            items.append(normalized)
    return items


def normalize_docbrain_items(payload: Any) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for item in ensure_list(payload):
        if not isinstance(item, dict) or not item.get("ok"):
            continue
        relative_output = collapse_ws(str(item.get("relative_output", "")))
        if not relative_output:
            continue
        items.append(
            {
                "title": collapse_ws(str(item.get("title", "Documento"))),
                "reference": f"acervo://{relative_output}",
                "microverso": item.get("microverso"),
                "summary_excerpt": collapse_ws(str(item.get("summary_excerpt", ""))),
                "sections_count": item.get("sections_count"),
                "tables_count": item.get("tables_count"),
                "document_id": item.get("document_id"),
            }
        )
    return items


def dedupe_signals(signals: list[dict[str, Any]], max_signals: int) -> list[dict[str, Any]]:
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    kept: list[dict[str, Any]] = []

    def sort_key(item: dict[str, Any]) -> tuple[str, str, str]:
        return (
            item.get("published_at", ""),
            item.get("source", ""),
            item.get("title", ""),
        )

    for item in sorted(signals, key=sort_key, reverse=True):
        url_key = item.get("url_normalized", "")
        title_key = item.get("title_normalized", "")
        if url_key in seen_urls or title_key in seen_titles:
            continue
        seen_urls.add(url_key)
        seen_titles.add(title_key)
        kept.append(item)
        if len(kept) >= max_signals:
            break
    return kept


def build_focus(scope: str, research_context: dict[str, Any], internal_context: dict[str, Any]) -> dict[str, Any]:
    query_terms = research_context.get("query_terms") or []
    focus = {
        "scope": scope,
        "sector_slug": research_context.get("sector_slug"),
        "region": research_context.get("region"),
        "query_terms": query_terms,
    }
    if scope == "micro":
        focus["public_client_name"] = research_context.get("public_client_name")
        focus["cliente_id"] = internal_context.get("cliente_id")
        focus["seller_id"] = internal_context.get("seller_id")
    return focus


def build_prompt_packet(
    scope: str,
    research_context: dict[str, Any],
    internal_context: dict[str, Any],
    counts: dict[str, int],
    documents: list[dict[str, Any]],
) -> dict[str, Any]:
    sector = research_context.get("sector_slug") or "setor"
    region = research_context.get("region") or "região"
    objective = f"Curar notícias de {sector} em {region} para publicação no Sales-AI via Rota B."
    if scope == "micro":
        objective = (
            f"Curar notícias de {sector} em {region} relevantes ao cliente "
            f"{research_context.get('public_client_name') or internal_context.get('cliente_id')} para publicação micro no Sales-AI."
        )
    constraints = [
        "Não publicar sem evidência citável.",
        "Priorizar fatos recentes, específicos e acionáveis.",
        "Para escopo micro, exigir ligação explícita com o cliente-alvo.",
        "O payload final deve respeitar o contrato canônico do writer Sales-AI.",
        "O DataBrain não é processo ativo; use-o apenas como harness sob demanda.",
    ]
    if documents:
        constraints.append("Usar documentos DocBrain apenas como contexto complementar; não tratá-los como notícia pública por si só.")
    return {
        "objective": objective,
        "counts": counts,
        "constraints": constraints,
        "writer_contract": {
            "tool": "sales-ai.publish_noticia",
            "required_fields": [
                "titulo",
                "fonte",
                "url",
                "publicado_em",
                "tipo_fonte",
                "impacto",
                "escopo",
                "valido_ate",
            ],
            "micro_requires": ["cliente_id"],
        },
        "harness_contract": {
            "job_context_schema": "projetob/news-job-context/v1",
            "batch_schema": "projetob/news-batch/v1",
            "preferred_cli_flow": [
                "databrain news context",
                "databrain news targets",
                "databrain news guard",
                "databrain news receipt",
                "databrain news expire-plan",
            ],
        },
    }


def build_dossier(
    job_context: dict[str, Any],
    *,
    crawler_payloads: list[Any],
    agent_reach_payloads: list[Any],
    docbrain_payloads: list[Any],
    max_signals: int = DEFAULT_MAX_SIGNALS,
) -> dict[str, Any]:
    scope = str(job_context.get("scope") or "macro")
    research_context = job_context.get("research_context") or {}
    internal_context = job_context.get("internal_context") or {}

    crawler_signals = [signal for payload in crawler_payloads for signal in normalize_crawler_items(payload)]
    agent_signals = [signal for payload in agent_reach_payloads for signal in normalize_agent_reach_items(payload)]
    documents = [item for payload in docbrain_payloads for item in normalize_docbrain_items(payload)]

    signals = dedupe_signals(crawler_signals + agent_signals, max_signals=max_signals)
    counts = {
        "crawler_brasil": len(crawler_signals),
        "agent_reach": len(agent_signals),
        "docbrain": len(documents),
        "signals_after_dedupe": len(signals),
    }

    return {
        "schema": SCHEMA,
        "generated_at": now_iso(),
        "focus": build_focus(scope, research_context, internal_context),
        "job_context": {
            "schema": job_context.get("schema") or "projetob/news-job-context/v1",
            "scope": scope,
            "research_context": research_context,
            "internal_context": internal_context,
        },
        "source_counts": counts,
        "signals": signals,
        "documents": documents,
        "prompt_packet": build_prompt_packet(scope, research_context, internal_context, counts, documents),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="build_dossier",
        description="Build a Route B news dossier from previously collected JSON payloads.",
    )
    parser.add_argument("--job-context", required=True, help="Path to DataBrain news-job-context JSON")
    parser.add_argument("--crawler", action="append", default=[], help="Path to crawler-brasil JSON payload")
    parser.add_argument("--agent-reach", action="append", default=[], help="Path to Agent-Reach JSON payload")
    parser.add_argument("--docbrain", action="append", default=[], help="Path to DocBrain adapter JSON payload")
    parser.add_argument("--max-signals", type=int, default=DEFAULT_MAX_SIGNALS, help="Maximum number of deduped signals")
    parser.add_argument("--output", choices=["json", "pretty"], default="json", help="Stdout format")
    parser.add_argument("--output-file", help="Optional file path for the resulting dossier")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    dossier = build_dossier(
        load_json(args.job_context),
        crawler_payloads=[load_json(path) for path in args.crawler],
        agent_reach_payloads=[load_json(path) for path in args.agent_reach],
        docbrain_payloads=[load_json(path) for path in args.docbrain],
        max_signals=args.max_signals,
    )
    write_json(dossier, args.output_file, pretty=args.output == "pretty")
    if args.output_file and args.output == "json":
        Path(args.output_file).write_text(json.dumps(dossier, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
