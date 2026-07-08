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


def scan(
    acervo: str | Path,
    *,
    today: date | str | None = None,
    stale_days: int = 90,
    upcoming_days: int = 7,
) -> dict[str, Any]:
    """Return a read-only Phase-4 consolidation queue.

    Buckets map to 08-write-policy.md §6:
    - intentions_due / intentions_upcoming: prospective memory sweep;
    - open_disputes: weekly digest surface;
    - review_due: review_after expiries;
    - stale_volatile: use-decay candidates for syndic review;
    - drafts: trust/risk-gated items awaiting approval;
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
        "drafts": [],
    }

    title_seen: dict[tuple[str | None, str], str] = {}
    duplicate_titles: list[dict[str, Any]] = []

    for row in _rows(root):
        rel = row["path"]
        fm, _body = read_frontmatter(root, rel)
        status = row.get("status") or fm.get("status") or "active"
        obj_type = row.get("type") or fm.get("type")
        title = (row.get("title") or fm.get("title") or "").strip()
        micro = row.get("microverso")

        if title:
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
        if cls == "volátil" and status == "active":
            last_accessed = parse_date(fm.get("last_accessed_at")) or parse_date(fm.get("updated")) or parse_date(fm.get("created_at"))
            age = _days_between(last_accessed, as_of)
            if last_accessed is not None and age is not None and age > stale_days:
                buckets["stale_volatile"].append(
                    _compact_item(row, fm, reason=f"volatile object inactive >{stale_days}d", last_seen=last_accessed.isoformat(), days_inactive=age)
                )

    buckets["duplicate_titles"] = duplicate_titles
    counts = {name: len(items) for name, items in buckets.items()}
    return {
        "ok": True,
        "operation": "consolidation_scan",
        "acervo_root": str(root),
        "as_of": as_of.isoformat(),
        "stale_days": stale_days,
        "upcoming_days": upcoming_days,
        "counts": counts,
        "buckets": {name: sorted(items, key=lambda it: (it.get("microverso") or "", it.get("path") or "")) for name, items in buckets.items()},
        "next_actions": [
            "Distill significant sessions into episodes only after curator/agent judgment.",
            "Resolve open disputes in the weekly maintenance digest; executive decides genuine disputes.",
            "Sweep due intentions: mark done/dropped/expired only through governed write verbs.",
            "Review stale volatile objects before syndic quarantine; perene/macro/raw remain immune.",
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only Phase-4 consolidation scan for the Acervo")
    parser.add_argument("--acervo", help="Acervo root (default: resolver do catálogo)")
    parser.add_argument("--today", help="Data de corte YYYY-MM-DD")
    parser.add_argument("--stale-days", type=int, default=90)
    parser.add_argument("--upcoming-days", type=int, default=7)
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    sub = parser.add_subparsers(dest="cmd")
    sub.add_parser("scan")
    args = parser.parse_args(argv)

    acervo = acervo_catalog.resolve_acervo_root(args.acervo)
    payload = scan(acervo, today=args.today, stale_days=args.stale_days, upcoming_days=args.upcoming_days)
    if args.format == "markdown":
        print(render_markdown(payload), end="")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
