"""Phase 4 write-side — H12 use-decay: retrieval journaling + the use_decay
consolidation bucket (replaces pure time-decay with 'never retrieved in N days').
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOLS = REPO / "acervo" / "global" / "tools"
FIXTURE = REPO / "tests" / "memory-eval" / "fixture" / "acervo"

sys.path.insert(0, str(TOOLS))

import acervo_catalog  # noqa: E402
import acervo_consolidation  # noqa: E402
import acervo_retrieve  # noqa: E402

AS_OF = "2026-07-08"


def _vol(title: str, created_at: str, cls: str = "volátil", type_: str = "knowledge") -> str:
    return (
        "---\n"
        "schema: acervo/v0.2\n"
        f"type: {type_}\n"
        f"title: {title}\n"
        f"description: {title}\n"
        "tags: [test]\n"
        f"class: {cls}\n"
        "status: active\n"
        "epistemic: fact\n"
        f"created_at: {created_at}\n"
        f"last_accessed_at: {AS_OF}T00:00:00Z\n"  # fresh access → NOT stale by time-decay
        "---\n\n"
        f"# {title}\n"
    )


def _write_journal(root: Path, events: list[dict]) -> None:
    j = root / "global" / "tools" / "state" / "retrieval-journal.jsonl"
    j.parent.mkdir(parents=True, exist_ok=True)
    j.write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")


@pytest.fixture()
def acervo(tmp_path: Path) -> Path:
    root = tmp_path / "acervo"
    shutil.copytree(FIXTURE, root)
    return root


# --------------------------------------------------------- retrieval journal

def test_retrieval_writes_journal(acervo: Path) -> None:
    acervo_catalog.build_catalog(acervo)
    result = acervo_retrieve.Retriever(acervo).retrieve("proposta", "global")
    journal = acervo_retrieve.retrieval_journal_path(acervo)
    assert journal.is_file()
    events = [json.loads(l) for l in journal.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(events) == 1
    ev = events[0]
    assert ev["scope"] == "global" and "paths" in ev and "ts" in ev
    # Logged paths mirror the packed result items.
    assert ev["paths"] == [it["path"] for it in result.get("items", [])]


# ------------------------------------------------------------- use_decay bucket

def _scan_with(acervo: Path, journal_events: list[dict]):
    base = acervo / "micro" / "operacoes" / "knowledge"
    base.mkdir(parents=True, exist_ok=True)
    (base / "never.md").write_text(_vol("Nunca recuperado", "2025-12-20T00:00:00Z"), encoding="utf-8")
    (base / "recent.md").write_text(_vol("Recuperado recente", "2025-12-20T00:00:00Z"), encoding="utf-8")
    (base / "young.md").write_text(_vol("Volátil jovem", "2026-07-01T00:00:00Z"), encoding="utf-8")
    (base / "perene.md").write_text(_vol("Perene", "2025-12-20T00:00:00Z", cls="perene"), encoding="utf-8")
    _write_journal(acervo, journal_events)
    acervo_catalog.build_catalog(acervo)
    return acervo_consolidation.scan(acervo, today=AS_OF, use_decay_days=180)


def test_use_decay_cold_start_guard(acervo: Path) -> None:
    # Journal spans < 180d → not enough history → nothing flagged, honest reason.
    payload = _scan_with(acervo, [{"ts": "2026-07-01T00:00:00+00:00", "paths": []}])
    assert payload["counts"]["use_decay"] == 0
    assert payload["use_decay_eval"]["evaluated"] is False
    assert "insufficient history" in payload["use_decay_eval"]["reason"]


def test_use_decay_flags_unretrieved_volatile(acervo: Path) -> None:
    # Journal spans > 180d (earliest 2026-01-01). 'recent' retrieved inside the
    # window; 'never' never retrieved; 'young' too new; 'perene' immune.
    payload = _scan_with(acervo, [
        {"ts": "2026-01-01T00:00:00+00:00", "paths": []},  # span setter
        {"ts": "2026-07-01T00:00:00+00:00", "paths": ["micro/operacoes/knowledge/recent.md"]},
    ])
    assert payload["use_decay_eval"]["evaluated"] is True
    flagged = {it["path"] for it in payload["buckets"]["use_decay"]}
    assert "micro/operacoes/knowledge/never.md" in flagged
    assert "micro/operacoes/knowledge/recent.md" not in flagged
    assert "micro/operacoes/knowledge/young.md" not in flagged
    assert "micro/operacoes/knowledge/perene.md" not in flagged


def test_use_decay_digest_advisory(acervo: Path) -> None:
    payload = _scan_with(acervo, [
        {"ts": "2026-01-01T00:00:00+00:00", "paths": []},
    ])
    digest = acervo_consolidation.render_digest(payload)
    # never + recent are both unretrieved-and-old here → advisory line appears.
    assert "Use-decay" in digest
