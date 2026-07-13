#!/usr/bin/env python3
"""Phase 7 human/agent interface over the canonical Acervo.

Read-only surfaces:
- briefing(): due intentions, disputes, drafts, recent episodes, active context
  heads, and optional calendar events under the 4k-token briefing budget.
- posture(): typed context packs for decision and research postures.

The module reuses the Phase 3/4 retrieval and consolidation control planes. It
never invents content and every surfaced item retains its canonical path.
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

import acervo_catalog
import acervo_consolidation
import acervo_retrieve
from acervo_hindsight_index import split_frontmatter

BRIEFING_BUDGET = 4000
POSTURE_BUDGET = 12000
CHARS_PER_TOKEN = 4

POSTURE_TYPES = {
    "decision": {"contract", "decision", "conflict", "entity", "intention", "knowledge"},
    "research": {"reflection", "conflict", "decision", "knowledge", "episode"},
}
POSTURE_PRIORITY = {
    "decision": {"contract": 6, "conflict": 5, "decision": 4, "entity": 3, "intention": 2, "knowledge": 1},
    "research": {"reflection": 6, "conflict": 5, "decision": 4, "knowledge": 3, "episode": 2},
}


def _day(value: date | str | None) -> date:
    if isinstance(value, date):
        return value
    if value:
        return date.fromisoformat(str(value)[:10])
    return datetime.now(timezone.utc).date()


def _tokens(text: str) -> int:
    return max(1, (len(text) + CHARS_PER_TOKEN - 1) // CHARS_PER_TOKEN)


def _scope_ok(item: dict[str, Any], scopes: set[str] | None) -> bool:
    if not scopes:
        return True
    micro = item.get("microverso")
    return micro in scopes or micro in (None, "", "global", "shared")


def _active_scopes(root: Path, requested: list[str] | None) -> list[str]:
    if requested:
        return sorted(dict.fromkeys(requested))
    micro = root / "micro"
    if not micro.is_dir():
        return []
    return sorted(
        p.name for p in micro.iterdir()
        if p.is_dir() and not p.name.startswith("_")
    )


def _calendar_events(path: str | Path | None, as_of: date) -> tuple[list[dict[str, Any]], str]:
    if not path:
        return [], "not_configured"
    source = Path(path).expanduser()
    if not source.is_file():
        return [], "missing"
    data = json.loads(source.read_text(encoding="utf-8"))
    events = data.get("events", data) if isinstance(data, dict) else data
    if not isinstance(events, list):
        raise ValueError("calendar JSON must be a list or {'events': [...]}")
    selected = []
    for event in events:
        if not isinstance(event, dict):
            continue
        start = str(event.get("start") or event.get("date") or "")
        if start[:10] == as_of.isoformat():
            selected.append({
                "title": event.get("title") or event.get("summary") or "Evento",
                "start": start,
                "source": str(source),
            })
    return sorted(selected, key=lambda x: x["start"]), "joined"


def _recent_episodes(root: Path, rows: list[dict[str, Any]], as_of: date,
                     scopes: set[str] | None, since_hours: int) -> list[dict[str, Any]]:
    cutoff = datetime.combine(as_of, datetime.min.time(), tzinfo=timezone.utc) - timedelta(
        hours=max(0, since_hours - 24)
    )
    items: list[dict[str, Any]] = []
    for row in rows:
        if row.get("type") != "episode" or (row.get("status") or "active") != "active":
            continue
        item = dict(row)
        if not _scope_ok(item, scopes):
            continue
        stamp = str(row.get("observed_at") or row.get("created_at") or "")
        try:
            dt = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        except ValueError:
            try:
                dt = datetime.combine(date.fromisoformat(stamp[:10]), datetime.min.time(), tzinfo=timezone.utc)
            except ValueError:
                continue
        end = datetime.combine(as_of + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)
        if cutoff <= dt < end:
            items.append({
                "path": row["path"], "title": row.get("title") or Path(row["path"]).stem,
                "microverso": row.get("microverso"), "observed_at": stamp,
                "reason": "recent episode",
            })
    return sorted(items, key=lambda x: x["observed_at"], reverse=True)


def _context_heads(root: Path, scopes: list[str]) -> list[dict[str, Any]]:
    heads = []
    for scope in scopes:
        rel = f"micro/{scope}/context/current-state.md"
        path = root / rel
        if not path.is_file():
            continue
        fm, body = split_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        summary = str(fm.get("description") or "").strip()
        if not summary:
            summary = next((line.lstrip("# ").strip() for line in body.splitlines() if line.strip()), "")
        heads.append({"path": rel, "title": fm.get("title") or scope, "microverso": scope, "summary": summary})
    return heads


def render_briefing(payload: dict[str, Any], *, compact: bool = False) -> str:
    sections = payload["sections"]
    lines = [f"☀️ Briefing — {payload['as_of']}"]
    if compact:
        queue: list[str] = []
        for item in sections["intentions_due"]:
            queue.append(f"🔴 [{item.get('microverso') or 'global'}] {item['title']} — {item.get('due')} ({item['path']})")
        for item in sections["intentions_upcoming"]:
            queue.append(f"🟠 [{item.get('microverso') or 'global'}] {item['title']} — {item.get('due')} ({item['path']})")
        for item in sections["open_disputes"]:
            queue.append(f"⚠ [{item.get('microverso') or 'global'}] Resolver: {item['title']} ({item['path']})")
        for item in sections["drafts"]:
            queue.append(f"📝 [{item.get('microverso') or 'global'}] Aprovar/rejeitar: {item['title']} ({item['path']})")
        for event in sections["agenda"]:
            queue.append(f"📅 {event['start']} — {event['title']}")
        for item in sections["recent_episodes"]:
            queue.append(f"• [{item.get('microverso') or 'global'}] {item['title']} ({item['path']})")
        if not queue:
            queue = ["Sem ações, disputas, drafts, agenda ou episódios recentes registrados."]
        return "\n".join(lines + queue[:9])

    def section(title: str, key: str, formatter) -> None:
        lines.extend(["", f"## {title}"])
        items = sections[key]
        if not items:
            lines.append("- Nenhum registro.")
        else:
            lines.extend(f"- {formatter(x)}" for x in items)

    section("Ações vencidas", "intentions_due", lambda x: f"[{x.get('microverso') or 'global'}] {x['title']} — due {x.get('due')} · `{x['path']}`")
    section("Próximos 7 dias", "intentions_upcoming", lambda x: f"[{x.get('microverso') or 'global'}] {x['title']} — due {x.get('due')} · `{x['path']}`")
    section("Disputas abertas", "open_disputes", lambda x: f"[{x.get('microverso') or 'global'}] {x['title']} — qual lado vale? · `{x['path']}`")
    section("Drafts aguardando aprovação", "drafts", lambda x: f"[{x.get('microverso') or 'global'}] {x['title']} — aprovar ou rejeitar? · `{x['path']}`")
    section("Agenda", "agenda", lambda x: f"{x['start']} — {x['title']} · `{x['source']}`")
    section("Últimas 24h", "recent_episodes", lambda x: f"[{x.get('microverso') or 'global'}] {x['title']} · `{x['path']}`")
    section("Estado dos domínios", "context_heads", lambda x: f"[{x['microverso']}] {x['summary']} · `{x['path']}`")
    if payload.get("omitted_count"):
        lines.extend(["", f"> {payload['omitted_count']} item(ns) omitidos pelo orçamento; consulte o JSON ou os paths sob demanda."])
    return "\n".join(lines)


def briefing(acervo_root: str | Path, *, today: date | str | None = None,
             scopes: list[str] | None = None, compact: bool = False,
             budget_tokens: int = BRIEFING_BUDGET, since_hours: int = 24,
             calendar_file: str | Path | None = None) -> dict[str, Any]:
    root = Path(acervo_root).expanduser().resolve()
    as_of = _day(today)
    selected_scopes = _active_scopes(root, scopes)
    scope_set = set(selected_scopes) if scopes else None
    scan = acervo_consolidation.scan(root, today=as_of.isoformat())
    rows = acervo_catalog.query_catalog(root, limit=100_000)
    agenda, calendar_status = _calendar_events(calendar_file, as_of)
    sections = {
        key: [x for x in scan["buckets"][key] if _scope_ok(x, scope_set)]
        for key in ("intentions_due", "intentions_upcoming", "open_disputes", "drafts")
    }
    sections.update({
        "agenda": agenda,
        "recent_episodes": _recent_episodes(root, rows, as_of, scope_set, since_hours),
        "context_heads": _context_heads(root, selected_scopes),
    })
    payload: dict[str, Any] = {
        "ok": True, "operation": "briefing", "as_of": as_of.isoformat(),
        "scopes": selected_scopes, "calendar_status": calendar_status,
        "budget_tokens": budget_tokens, "compact": compact, "sections": sections,
    }
    rendered = render_briefing(payload, compact=compact)
    # Hard budget: compact is already capped at 10 lines; detailed degrades by
    # trimming context heads, then recent episodes, while retaining governance.
    while _tokens(rendered) > budget_tokens and sections["context_heads"]:
        sections["context_heads"].pop()
        payload["omitted_count"] = payload.get("omitted_count", 0) + 1
        rendered = render_briefing(payload, compact=compact)
    while _tokens(rendered) > budget_tokens and sections["recent_episodes"]:
        sections["recent_episodes"].pop()
        payload["omitted_count"] = payload.get("omitted_count", 0) + 1
        rendered = render_briefing(payload, compact=compact)
    # Governance queues degrade last, but the budget is a hard contract. Items
    # omitted from prose remain in the machine-readable scan available through
    # consolidation-scan; the briefing declares the omission explicitly.
    for key in ("agenda", "drafts", "intentions_upcoming", "open_disputes", "intentions_due"):
        while _tokens(rendered) > budget_tokens and sections[key]:
            sections[key].pop()
            payload["omitted_count"] = payload.get("omitted_count", 0) + 1
            rendered = render_briefing(payload, compact=compact)
    payload["markdown"] = rendered
    payload["tokens_est"] = _tokens(rendered)
    payload["citations"] = sorted({
        f"Acervo: {item['path']}" for items in sections.values() for item in items
        if isinstance(item, dict) and item.get("path") and item["path"] in rendered
    })
    return payload


def posture(acervo_root: str | Path, *, mode: str, query: str, scope: str,
            allow_scopes: list[str] | None = None, budget_tokens: int = POSTURE_BUDGET,
            k: int = 8) -> dict[str, Any]:
    if mode not in POSTURE_TYPES:
        raise ValueError("mode must be 'decision' or 'research'")
    retriever = acervo_retrieve.Retriever(acervo_root)
    terms = acervo_retrieve.query_terms(query)
    allowed_types = POSTURE_TYPES[mode]
    scored: list[tuple[float, str]] = []
    for rel, row in retriever.objects.items():
        if row.get("type") not in allowed_types or (row.get("status") or "active") != "active":
            continue
        if not retriever._visible(rel, scope, allow_scopes):
            continue
        matched = retriever.matched_terms(rel, terms)
        if not matched or not retriever.above_floor(matched):
            continue
        score = len(matched) + POSTURE_PRIORITY[mode].get(row.get("type"), 0)
        scored.append((score, rel))
    items = [
        retriever._make_item(rel, score, f"posture-{mode}", "result")
        for score, rel in sorted(scored, key=lambda x: (-x[0], x[1]))[:k]
    ]
    packed, total = acervo_retrieve.pack(items, budget_tokens)
    prompts = {
        "decision": "Compare precedentes, contratos, disputas e stakes. Proponha opções e um esqueleto de ADR; o executivo decide.",
        "research": "Evidencie tensões, perguntas abertas, alternativas rejeitadas e lacunas. Não feche conclusão prematuramente.",
    }
    return {
        "ok": True, "operation": "posture", "mode": mode, "query": query,
        "scope": scope, "allow_scopes": list(allow_scopes or []),
        "found": bool(packed), "instruction": prompts[mode], "items": packed,
        "citations": [f"Acervo: {item['path']}" for item in packed],
        "total_tokens": total, "budget_tokens": budget_tokens,
        "message": None if packed else f"não há registro no Acervo para modo {mode} sobre: {query}",
    }
