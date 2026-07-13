#!/usr/bin/env python3
"""Reporta os loops de aprendizado da memória v2 (H7 + H12).

H7 — Governed auto-commit audit
  Janela padrão: 30 dias.
  Métrica: % de objetos auto-commitados depois corrigidos/revertidos.

H12 — Usefulness loop / use-decay
  Reusa o consolidation-scan para reportar se o journal já tem histórico
  suficiente e quantos candidatos a use-decay existem.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from acervoctl import load_tool_module


AUTO_SOURCE_TYPES = {"agent-inference", "executive"}
CORRECTION_STATES = {"superseded", "deprecated", "quarantined"}


@dataclass
class AuditItem:
    path: str
    title: str
    type: str | None
    status: str | None
    created_at: str | None
    signal: str | None = None
    detail: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "path": self.path,
            "title": self.title,
            "type": self.type,
            "status": self.status,
            "created_at": self.created_at,
        }
        if self.signal:
            payload["signal"] = self.signal
        if self.detail:
            payload["detail"] = self.detail
        return payload


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acervo-root", type=Path, required=True)
    parser.add_argument("--today", help="Data de corte (YYYY-MM-DD). Default: hoje UTC.")
    parser.add_argument("--window-days", type=int, default=30)
    parser.add_argument("--use-decay-days", type=int, default=180)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    return parser.parse_args(argv)


def utc_today() -> date:
    return datetime.now(timezone.utc).date()


def parse_day(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    text = str(value).strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        pass
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text).date()
    except ValueError:
        return None


def pct(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value * 100:.1f}%"


def norm_sources(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        value = [value]
    out: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, dict):
            out.append(item)
    return out


def is_auto_committed(fm: dict[str, Any]) -> bool:
    status = str(fm.get("status") or "active").strip().lower()
    if status == "draft":
        return False
    extraction = str(fm.get("extraction") or "").strip().lower()
    for src in norm_sources(fm.get("sources")):
        ref = str(src.get("ref") or "").strip()
        src_type = str(src.get("type") or "").strip().lower()
        if ref == "acervoctl://new-object":
            return True
        if extraction in {"agent", "executive"} and src_type in AUTO_SOURCE_TYPES:
            return True
    return False


def correction_signal(fm: dict[str, Any]) -> tuple[str, str] | None:
    status = str(fm.get("status") or "active").strip().lower()
    if fm.get("superseded_by") or status == "superseded":
        detail = str(fm.get("superseded_by") or "status:superseded")
        return "superseded", detail
    if fm.get("disputed_by"):
        return "disputed", str(fm.get("disputed_by"))
    if status == "deprecated" or fm.get("deprecated") is True or str(fm.get("deprecated", "")).lower() == "true":
        return "deprecated", str(fm.get("deprecated_reason") or "deprecated")
    if status == "quarantined" or fm.get("quarantined_at"):
        return "quarantined", str(fm.get("quarantine_reason") or fm.get("quarantined_at") or "quarantined")
    return None


def h7_verdict(ratio: float | None, total: int) -> str:
    if total == 0:
        return "no_data"
    if ratio is None:
        return "no_data"
    if ratio > 0.10:
        return "tighten"
    if ratio < 0.02:
        return "widen"
    return "hold"


def build_h7(root: Path, *, today: date, window_days: int, limit: int) -> dict[str, Any]:
    catalog = load_tool_module(root, "acervo_catalog")
    consolidation = load_tool_module(root, "acervo_consolidation")

    window_start = today - timedelta(days=window_days)
    candidates: list[AuditItem] = []
    corrected: list[AuditItem] = []
    stable: list[AuditItem] = []

    for path in catalog.iter_catalog_files(root):
        rel = path.relative_to(root).as_posix()
        try:
            fm, _body = consolidation.read_frontmatter(root, rel)
        except Exception:
            continue
        created = parse_day(fm.get("created_at") or fm.get("created") or fm.get("timestamp"))
        if created is None or created < window_start or created > today:
            continue
        if not is_auto_committed(fm):
            continue
        item = AuditItem(
            path=rel,
            title=str(fm.get("title") or path.stem),
            type=fm.get("type"),
            status=fm.get("status"),
            created_at=str(fm.get("created_at") or ""),
        )
        candidates.append(item)
        signal = correction_signal(fm)
        if signal:
            item.signal, item.detail = signal
            corrected.append(item)
        else:
            stable.append(item)

    corrected_count = len(corrected)
    total = len(candidates)
    ratio = (corrected_count / total) if total else None
    by_signal: dict[str, int] = {}
    for item in corrected:
        by_signal[item.signal or "unknown"] = by_signal.get(item.signal or "unknown", 0) + 1

    return {
        "window_days": window_days,
        "window_start": window_start.isoformat(),
        "window_end": today.isoformat(),
        "candidate_count": total,
        "corrected_count": corrected_count,
        "corrected_ratio": ratio,
        "verdict": h7_verdict(ratio, total),
        "thresholds": {
            "tighten_gt": 0.10,
            "widen_lt": 0.02,
        },
        "corrected_by_signal": by_signal,
        "corrected_items": [item.to_dict() for item in corrected[:limit]],
        "stable_items": [item.to_dict() for item in stable[:limit]],
    }


def build_h12(root: Path, *, today: date, use_decay_days: int, limit: int) -> dict[str, Any]:
    consolidation = load_tool_module(root, "acervo_consolidation")
    payload = consolidation.scan(root, today=today.isoformat(), use_decay_days=use_decay_days)
    return {
        "use_decay_days": use_decay_days,
        "candidate_count": payload["counts"].get("use_decay", 0),
        "evaluation": payload.get("use_decay_eval", {}),
        "candidates": payload["buckets"].get("use_decay", [])[:limit],
    }


def build_report(root: Path, *, today: date, window_days: int, use_decay_days: int, limit: int) -> dict[str, Any]:
    h7 = build_h7(root, today=today, window_days=window_days, limit=limit)
    h12 = build_h12(root, today=today, use_decay_days=use_decay_days, limit=limit)
    return {
        "ok": True,
        "acervo_root": str(root),
        "as_of": today.isoformat(),
        "h7": h7,
        "h12": h12,
    }


def render_markdown(report: dict[str, Any]) -> str:
    h7 = report["h7"]
    h12 = report["h12"]
    lines = [
        f"# Memory learning loops report ({report['as_of']})",
        "",
        "## H7 — Governed auto-commit audit",
        "",
        f"- Janela: `{h7['window_start']}` → `{h7['window_end']}` ({h7['window_days']} dias)",
        f"- Objetos auto-commitados auditados: **{h7['candidate_count']}**",
        f"- Corrigidos/revertidos: **{h7['corrected_count']}** ({pct(h7['corrected_ratio'])})",
        f"- Veredito: **{h7['verdict']}**",
        "",
    ]

    if h7["corrected_items"]:
        lines += [
            "### Itens corrigidos",
            "",
            "| Path | Signal | Detail |",
            "|---|---|---|",
        ]
        for item in h7["corrected_items"]:
            lines.append(
                f"| `{item['path']}` | {item.get('signal', '—')} | {item.get('detail', '—')} |"
            )
        lines.append("")
    else:
        lines += ["- Nenhum item corrigido/revertido dentro da janela.", ""]

    lines += [
        "## H12 — Usefulness loop / use-decay",
        "",
        f"- Threshold: `{h12['use_decay_days']}` dias",
        f"- Candidatos a use-decay: **{h12['candidate_count']}**",
        f"- Avaliado: **{str(h12['evaluation'].get('evaluated', False)).lower()}**",
    ]
    reason = h12["evaluation"].get("reason")
    if reason:
        lines.append(f"- Motivo: {reason}")
    span = h12["evaluation"].get("journal_span_days")
    if span is not None:
        lines.append(f"- Span do journal: `{span}` dias")
    lines.append("")

    if h12["candidates"]:
        lines += [
            "### Principais candidatos",
            "",
            "| Path | Days since retrieval | Reason |",
            "|---|---:|---|",
        ]
        for item in h12["candidates"]:
            days = item.get("days_since_retrieval")
            days_text = "—" if days is None else str(days)
            lines.append(
                f"| `{item['path']}` | {days_text} | {item.get('reason', '—')} |"
            )
        lines.append("")
    else:
        lines += ["- Nenhum candidato a use-decay no corte atual.", ""]

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.acervo_root.expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: acervo root não encontrado: {root}", file=sys.stderr)
        return 2
    today = parse_day(args.today) if args.today else utc_today()
    if today is None:
        print(f"ERROR: today inválido: {args.today!r}", file=sys.stderr)
        return 2
    report = build_report(
        root,
        today=today,
        window_days=args.window_days,
        use_decay_days=args.use_decay_days,
        limit=args.limit,
    )
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
