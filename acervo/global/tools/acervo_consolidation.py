#!/usr/bin/env python3
"""Acervo consolidation scan (Phase 4, read-only first cut).

The consolidation loop is the constructive counterpart to syndic/quarantine: it
surfaces what should be distilled, refreshed, reviewed, or resolved, without
mutating canonical memory. All findings are derived from Plane 1 Markdown plus
the disposable catalog.sqlite cache.

CLI: scan [--today YYYY-MM-DD] [--stale-days N] [--format json|markdown]
Exposed through: acervoctl consolidation-scan
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml

_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

import acervo_catalog  # noqa: E402
from acervo_hindsight_index import split_frontmatter  # noqa: E402

ACTIVE_LIKE = {"active", "draft"}
ISO_DATE_KEYS = ("last_accessed_at", "review_after", "due", "created_at")


def parse_date(value: Any) -> date | None:
    """Parse frontmatter dates/datetimes conservatively."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip().strip('"').strip("'")
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text).date()
    except ValueError:
        pass
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def today_utc() -> date:
    return datetime.now(timezone.utc).date()


def read_frontmatter(acervo: Path, rel: str) -> tuple[dict[str, Any], str]:
    text = (acervo / rel).read_text(encoding="utf-8", errors="replace")
    fm, body = split_frontmatter(text)
    if not isinstance(fm, dict):
        fm = {}
    return fm, body


def _compact_item(row: dict[str, Any], fm: dict[str, Any], *, reason: str, **extra: Any) -> dict[str, Any]:
    payload = {
        "path": row["path"],
        "title": row.get("title") or fm.get("title") or Path(row["path"]).stem,
        "type": row.get("type") or fm.get("type"),
        "status": row.get("status") or fm.get("status") or "active",
        "class": row.get("class") or fm.get("class"),
        "microverso": row.get("microverso"),
        "reason": reason,
    }
    payload.update({k: v for k, v in extra.items() if v is not None})
    return payload


def _days_between(a: date | None, b: date) -> int | None:
    if a is None:
        return None
    return (b - a).days


def _rows(acervo: Path) -> list[dict[str, Any]]:
    db = acervo_catalog.catalog_path(acervo)
    if not db.exists():
        acervo_catalog.build_catalog(acervo)
    return acervo_catalog.query_catalog(acervo, limit=100_000)


def _load_retrieval_history(root: Path, as_of: date) -> tuple[dict[str, date], int | None]:
    """Read the H12 retrieval journal → ({rel: last_retrieved_date}, span_days).

    span_days = age of the earliest logged event (None if the journal is absent
    or empty). Use-decay needs history that actually spans the decay window —
    otherwise a freshly-started journal would flag every object as 'never
    retrieved' (cold-start flood)."""
    journal = root / "global" / "tools" / "state" / "retrieval-journal.jsonl"
    last: dict[str, date] = {}
    earliest: date | None = None
    if not journal.is_file():
        return last, None
    try:
        lines = journal.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return last, None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        ev_date = parse_date(ev.get("ts"))
        if ev_date is None:
            continue
        if earliest is None or ev_date < earliest:
            earliest = ev_date
        for rel in ev.get("paths") or []:
            prev = last.get(rel)
            if prev is None or ev_date > prev:
                last[rel] = ev_date
    span = (as_of - earliest).days if earliest is not None else None
    return last, span


def _scan_quarantine(root: Path, as_of: date) -> list[dict[str, Any]]:
    """Quarantine purge notices, read directly from `.quarantine/` (a SKIP_PARTS
    dir the catalog never indexes). The notice repeats until acknowledged (09 §3)."""
    qdir = root / ".quarantine"
    notices: list[dict[str, Any]] = []
    if not qdir.is_dir():
        return notices
    for path in sorted(qdir.rglob("*.md")):
        if path.name in ("log.md", "index.md", "README.md"):
            continue
        try:
            fm, _body = read_frontmatter(root, str(path.relative_to(root)))
        except OSError:
            continue
        # Only genuinely quarantined files carry quarantine frontmatter; skip
        # docs/scaffolding that merely live under .quarantine/.
        if not (fm.get("quarantine_expires_at") or fm.get("quarantined_at")):
            continue
        expires = parse_date(fm.get("quarantine_expires_at"))
        notices.append({
            "path": str(path.relative_to(root)),
            "title": fm.get("title") or path.stem,
            "type": fm.get("type"),
            "quarantine_reason": fm.get("quarantine_reason"),
            "expires_at": expires.isoformat() if expires else None,
            "days_left": (expires - as_of).days if expires else None,
            "reason": "quarantine purge notice — restore or let it purge",
        })
    return notices


def scan(
    acervo: str | Path,
    *,
    today: date | str | None = None,
    stale_days: int = 90,
    upcoming_days: int = 7,
    use_decay_days: int = 180,
) -> dict[str, Any]:
    """Return a read-only Phase-4 consolidation queue.

    Buckets map to 08-write-policy.md §6:
    - intentions_due / intentions_upcoming: prospective memory sweep;
    - open_disputes: weekly digest surface;
    - review_due: review_after expiries;
    - stale_volatile: use-decay candidates for syndic review;
    - drafts: trust/risk-gated items awaiting approval;
    - purge_notices: quarantined files pending purge (restore-or-purge);
    - duplicate_titles: dedup audit candidates (advisory).
    """
    root = Path(acervo).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"Acervo root not found: {root}")
    as_of = parse_date(today) if today is not None else today_utc()
    if as_of is None:
        raise ValueError(f"today inválido: {today!r}")

    buckets: dict[str, list[dict[str, Any]]] = {
        "intentions_due": [],
        "intentions_upcoming": [],
        "open_disputes": [],
        "review_due": [],
        "stale_volatile": [],
        "use_decay": [],
        "drafts": [],
    }

    # H12 use-decay: replace pure time-decay with "never retrieved in N days".
    last_retrieved, journal_span = _load_retrieval_history(root, as_of)
    use_decay_ready = journal_span is not None and journal_span >= use_decay_days

    title_seen: dict[tuple[str | None, str], str] = {}
    duplicate_titles: list[dict[str, Any]] = []

    for row in _rows(root):
        rel = row["path"]
        fm, _body = read_frontmatter(root, rel)
        status = row.get("status") or fm.get("status") or "active"
        obj_type = row.get("type") or fm.get("type")
        title = (row.get("title") or fm.get("title") or "").strip()
        micro = row.get("microverso")

        deprecated = fm.get("deprecated") is True or str(fm.get("deprecated", "")).lower() == "true"
        # Dedup audit: only active/draft files count, and never macro/ — the identity
        # layer is git-governed (structural filenames like SOUL.md/soul.md legitimately
        # coexist), not memory-lifecycle managed. A superseded/deprecated file is already
        # resolved and must not re-surface as a duplicate.
        dedup_eligible = status in ACTIVE_LIKE and not deprecated and not rel.startswith("macro/")
        if title and dedup_eligible:
            key = (micro, title.casefold())
            previous = title_seen.get(key)
            if previous and previous != rel:
                duplicate_titles.append({
                    "microverso": micro,
                    "title": title,
                    "paths": sorted({previous, rel}),
                    "reason": "same title within the same microverso; dedup audit candidate",
                })
            else:
                title_seen[key] = rel

        if status == "draft":
            buckets["drafts"].append(_compact_item(row, fm, reason="draft awaiting trust/risk review"))

        if obj_type == "conflict" and status in ACTIVE_LIKE:
            buckets["open_disputes"].append(_compact_item(row, fm, reason="open conflict object"))

        due = parse_date(fm.get("due"))
        if obj_type == "intention" and status == "active" and due:
            delta = (due - as_of).days
            if delta < 0:
                buckets["intentions_due"].append(
                    _compact_item(row, fm, reason="intention overdue", due=due.isoformat(), days_overdue=abs(delta))
                )
            elif delta == 0:
                buckets["intentions_due"].append(
                    _compact_item(row, fm, reason="intention due today", due=due.isoformat(), days_until=0)
                )
            elif delta <= upcoming_days:
                buckets["intentions_upcoming"].append(
                    _compact_item(row, fm, reason="intention due soon", due=due.isoformat(), days_until=delta)
                )

        review_after = parse_date(fm.get("review_after"))
        if status == "active" and review_after and review_after <= as_of:
            buckets["review_due"].append(
                _compact_item(row, fm, reason="review_after reached", review_after=review_after.isoformat())
            )

        cls = row.get("class") or fm.get("class")
        # Use-decay applies to knowledge/context-like volatile objects; intentions
        # (due-swept) and conflicts (disputed) have their own governed lifecycles.
        if cls == "volátil" and status == "active" and obj_type not in ("intention", "conflict"):
            last_accessed = parse_date(fm.get("last_accessed_at")) or parse_date(fm.get("updated")) or parse_date(fm.get("created_at"))
            age = _days_between(last_accessed, as_of)
            if last_accessed is not None and age is not None and age > stale_days:
                buckets["stale_volatile"].append(
                    _compact_item(row, fm, reason=f"volatile object inactive >{stale_days}d", last_seen=last_accessed.isoformat(), days_inactive=age)
                )
            # Use-decay (H12): a volatile object older than the window that has
            # never — or not recently — been *retrieved* is a demotion candidate,
            # even if its last_accessed_at looks fresh. Guarded on journal history
            # so a cold-started journal doesn't flag everything.
            if use_decay_ready:
                created = parse_date(fm.get("created_at"))
                obj_age = _days_between(created, as_of)
                if obj_age is not None and obj_age > use_decay_days:
                    last_ret = last_retrieved.get(rel)
                    ret_age = _days_between(last_ret, as_of)
                    if last_ret is None or (ret_age is not None and ret_age > use_decay_days):
                        buckets["use_decay"].append(
                            _compact_item(
                                row, fm,
                                reason=f"volatile never/again retrieved in >{use_decay_days}d (use-decay, H12)",
                                last_retrieved=last_ret.isoformat() if last_ret else None,
                                days_since_retrieval=ret_age,
                            )
                        )

    buckets["purge_notices"] = _scan_quarantine(root, as_of)
    buckets["duplicate_titles"] = duplicate_titles
    counts = {name: len(items) for name, items in buckets.items()}
    return {
        "ok": True,
        "operation": "consolidation_scan",
        "acervo_root": str(root),
        "as_of": as_of.isoformat(),
        "stale_days": stale_days,
        "upcoming_days": upcoming_days,
        "use_decay_days": use_decay_days,
        "use_decay_eval": {
            "evaluated": use_decay_ready,
            "journal_span_days": journal_span,
            "threshold_days": use_decay_days,
            "reason": None if use_decay_ready else (
                "no retrieval journal yet" if journal_span is None
                else f"journal spans only {journal_span}d (< {use_decay_days}d) — insufficient history"
            ),
        },
        "counts": counts,
        "buckets": {name: sorted(items, key=lambda it: (it.get("microverso") or "", it.get("path") or "")) for name, items in buckets.items()},
        "next_actions": [
            "Distill significant sessions into episodes only after curator/agent judgment.",
            "Resolve open disputes in the weekly maintenance digest; executive decides genuine disputes.",
            "Sweep due intentions: mark done/dropped/expired only through governed write verbs.",
            "Review stale volatile objects before syndic quarantine; perene/macro/raw remain immune.",
            "Use-decay candidates are a syndic demotion signal (H12); they only appear once the retrieval journal spans the window.",
        ],
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Acervo Consolidation Scan",
        "",
        f"- Acervo: `{payload['acervo_root']}`",
        f"- Data de corte: `{payload['as_of']}`",
        f"- Stale threshold: `{payload['stale_days']}d`",
        "",
        "## Counts",
        "",
    ]
    for name, count in payload["counts"].items():
        lines.append(f"- `{name}`: {count}")
    lines.append("")

    for name, items in payload["buckets"].items():
        if not items:
            continue
        lines.extend([f"## {name}", ""])
        for item in items[:50]:
            title = item.get("title") or item.get("path")
            reason = item.get("reason", "")
            lines.append(f"- `{item.get('path')}` — {title} ({reason})")
        if len(items) > 50:
            lines.append(f"- … +{len(items) - 50} itens")
        lines.append("")

    lines.extend(["## Next actions", ""])
    for action in payload["next_actions"]:
        lines.append(f"- {action}")
    return "\n".join(lines).rstrip() + "\n"


def render_digest(payload: dict[str, Any]) -> str:
    """Weekly maintenance digest (09 §3): the one place the human governs. Each
    governable item is one line + one question. Read-only; degrades gracefully."""
    b = payload["buckets"]
    sections: list[tuple[str, str, Any]] = [
        ("open_disputes", "Disputas abertas — qual versão vale?",
         lambda it: f"**Qual vale?** (A / B / manter ambos)"),
        ("drafts", "Drafts pendentes — aprovar ou rejeitar?",
         lambda it: f"**Aprovar?** (aprovar / rejeitar)"),
        ("review_due", "Revisão de decisões (review_after venceu) — ainda vale?",
         lambda it: f"**Ainda verdadeiro?** (sim / atualizar / arquivar)"),
        ("stale_volatile", "Dormência (volátil inativo) — confirmar quarentena?",
         lambda it: f"({it.get('days_inactive')}d inativo) · **Quarentenar?** (sim / manter)"),
        ("purge_notices", "Avisos de purga — restaurar antes de expirar?",
         lambda it: (f"({'VENCIDO' if (it.get('days_left') is not None and it['days_left'] < 0) else (str(it.get('days_left')) + 'd restantes' if it.get('days_left') is not None else 'sem data')}) · "
                     "**Restaurar?** (restaurar / deixar purgar)")),
    ]
    body: list[str] = []
    asked = 0
    for name, heading, question in sections:
        items = b.get(name) or []
        if not items:
            continue
        body.extend([f"## {heading}", ""])
        for it in items:
            asked += 1
            title = it.get("title") or it.get("path")
            body.append(f"- `{it.get('path')}` — {title} · {question(it)}")
        body.append("")

    du = payload["counts"].get("intentions_due", 0)
    up = payload["counts"].get("intentions_upcoming", 0)
    if du or up:
        body.extend(["## Intenções (informativo — varridas pelo sweep governado)", "",
                     f"- {du} vencida(s)/hoje · {up} próxima(s)", ""])
    dups = payload["counts"].get("duplicate_titles", 0)
    if dups:
        body.extend(["## Dedup (advisory — sem ação humana obrigatória)", "",
                     f"- {dups} título(s) duplicado(s) para auditoria do agente", ""])
    decay = payload["counts"].get("use_decay", 0)
    if decay:
        body.extend(["## Use-decay (advisory — sinal p/ o síndico, H12)", "",
                     f"- {decay} objeto(s) volátil(eis) sem uso há muito tempo (candidatos a rebaixamento)", ""])

    header = [
        "# Digest semanal de manutenção",
        "",
        f"- Data de corte: `{payload['as_of']}`",
        f"- **{asked} item(ns) pedindo sua decisão.** Alvo: < 5 min.",
        "- Ignorar é seguro: nada é commitado ou purgado em silêncio; o aviso repete até você agir.",
        "",
    ]
    if asked == 0:
        body = ["_Nada requer sua governança esta semana._ ✅", ""]
    return "\n".join(header + body).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only Phase-4 consolidation scan for the Acervo")
    parser.add_argument("--acervo", help="Acervo root (default: resolver do catálogo)")
    parser.add_argument("--today", help="Data de corte YYYY-MM-DD")
    parser.add_argument("--stale-days", type=int, default=90)
    parser.add_argument("--upcoming-days", type=int, default=7)
    parser.add_argument("--use-decay-days", type=int, default=180)
    parser.add_argument("--format", choices=["json", "markdown", "digest"], default="json")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("scan")
    args = parser.parse_args(argv)

    acervo = acervo_catalog.resolve_acervo_root(args.acervo)
    payload = scan(acervo, today=args.today, stale_days=args.stale_days,
                   upcoming_days=args.upcoming_days, use_decay_days=args.use_decay_days)
    if args.format == "markdown":
        print(render_markdown(payload), end="")
    elif args.format == "digest":
        print(render_digest(payload), end="")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
