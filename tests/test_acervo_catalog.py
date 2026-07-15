"""Tests for acervo/global/tools/acervo_catalog.py (Phase 1: catalog + doctor)."""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOLS = REPO / "acervo" / "global" / "tools"
ACERVOCTL = REPO / "scripts" / "acervoctl.py"

sys.path.insert(0, str(TOOLS))

import acervo_catalog  # noqa: E402


def _v02(type_: str, title: str, description: str, extra: str = "", status: str = "active") -> str:
    return (
        "---\n"
        "schema: acervo/v0.2\n"
        f"type: {type_}\n"
        f"title: {title}\n"
        f"description: {description}\n"
        "tags: [test]\n"
        "class: perene\n"
        f"status: {status}\n"
        "created_at: 2026-07-01T00:00:00Z\n"
        f"{extra}"
        "---\n\n"
        f"# {title}\n\nCorpo de teste.\n"
    )


@pytest.fixture()
def mini_acervo(tmp_path: Path) -> Path:
    """Synthetic acervo: 2 microversos + global, with planted problems.

    Planted problems (doctor must find exactly these):
      ERROR broken-link      micro/alpha/decisions/broken-relates.md
      ERROR V2-020           micro/alpha/knowledge/wrong-home.md
      ERROR V2-030           micro/beta/context/lonely-superseded.md
      WARN  broken-wikilink  micro/beta/knowledge/v1-legacy.md
    Plus a CORRECT superseded pair (pricing-2025/2026) that must NOT be flagged.
    """
    acervo = tmp_path / "acervo"
    files = {
        # --- micro/alpha (5 objects) ---
        "micro/alpha/knowledge/coffee-preference.md": _v02(
            "knowledge", "Coffee preference", "Executive coffee habits",
        ).replace(
            "Corpo de teste.",
            "The xenon marmalade protocol governs mornings. See [[pricing-2026]].",
        ),
        "micro/alpha/knowledge/pricing-2025.md": _v02(
            "knowledge", "Pricing 2025", "Old price table",
            extra="superseded_by: micro/alpha/knowledge/pricing-2026.md\n",
            status="superseded",
        ),
        "micro/alpha/knowledge/pricing-2026.md": _v02(
            "knowledge", "Pricing 2026", "Current price table",
            extra="supersedes:\n  - micro/alpha/knowledge/pricing-2025.md\n",
        ),
        "micro/alpha/decisions/broken-relates.md": _v02(
            "decision", "Broken relates decision", "Decision with dangling link",
            extra="relates_to:\n  - micro/alpha/knowledge/nonexistent.md\n",
        ),
        "micro/alpha/knowledge/wrong-home.md": _v02(
            "decision", "Wrong home object", "Decision living in knowledge dir",
        ),
        # --- micro/beta (3 objects) ---
        "micro/beta/context/lonely-superseded.md": _v02(
            "context", "Lonely superseded", "Superseded without pointer",
            status="superseded",
        ),
        "micro/beta/knowledge/v1-legacy.md": (
            "---\n"
            "type: knowledge\n"
            "title: Legacy v1 note\n"
            "description: Pre-v0.2 file without schema field\n"
            "tags: [legacy]\n"
            "timestamp: 2026-06-01\n"
            "class: volátil\n"
            "created_at: 2026-06-01T00:00:00Z\n"
            "---\n\n"
            "Aponta para [[ghost-note]] que nunca existiu.\n"
        ),
        "micro/beta/decisions/beta-decision.md": _v02(
            "decision", "Beta decision", "A fine decision",
        ),
        # --- global (1 object) ---
        "global/knowledge/global-note.md": _v02(
            "knowledge", "Global note", "Universal knowledge",
        ),
        # --- must be skipped ---
        "_inbox/queued.md": "---\ntitle: Queued\n---\nNot memory yet.\n",
        "micro/alpha/_meta/log.md": "# Log\n- CREATED whatever\n",
    }
    for rel, content in files.items():
        path = acervo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return acervo


EXPECTED_OBJECTS = 9  # 5 alpha + 3 beta + 1 global; _inbox + _meta/log.md skipped


def test_build_counts_and_idempotence(mini_acervo: Path) -> None:
    result = acervo_catalog.build_catalog(mini_acervo)
    assert result["objects"] == EXPECTED_OBJECTS
    assert result["parse_errors"] == []
    assert (mini_acervo / "global/tools/state/catalog.sqlite").exists()

    conn = sqlite3.connect(mini_acervo / "global/tools/state/catalog.sqlite")
    rows = conn.execute("SELECT COUNT(*) FROM objects").fetchone()[0]
    links = conn.execute("SELECT COUNT(*) FROM links").fetchone()[0]
    skipped = conn.execute(
        "SELECT COUNT(*) FROM objects WHERE path LIKE '_inbox/%' OR path LIKE '%_meta/log.md'"
    ).fetchone()[0]
    conn.close()
    assert rows == EXPECTED_OBJECTS
    assert skipped == 0
    # links: superseded_by + supersedes + relates_to + 2 wikilinks = 5
    assert links == 5

    # rebuild is idempotent: same counts, no duplicate rows
    again = acervo_catalog.build_catalog(mini_acervo)
    assert again["objects"] == result["objects"]
    assert again["links"] == result["links"]


def test_query_filters(mini_acervo: Path) -> None:
    acervo_catalog.build_catalog(mini_acervo)
    knowledge_alpha = acervo_catalog.query_catalog(mini_acervo, type_="knowledge", microverso="alpha")
    assert {r["path"] for r in knowledge_alpha} == {
        "micro/alpha/knowledge/coffee-preference.md",
        "micro/alpha/knowledge/pricing-2025.md",
        "micro/alpha/knowledge/pricing-2026.md",
    }
    superseded = acervo_catalog.query_catalog(mini_acervo, status="superseded")
    assert {r["path"] for r in superseded} == {
        "micro/alpha/knowledge/pricing-2025.md",
        "micro/beta/context/lonely-superseded.md",
    }
    global_layer = acervo_catalog.query_catalog(mini_acervo, layer="global")
    assert [r["path"] for r in global_layer] == ["global/knowledge/global-note.md"]
    assert global_layer[0]["tags"] == ["test"]


def test_fts_finds_planted_phrase(mini_acervo: Path) -> None:
    acervo_catalog.build_catalog(mini_acervo)
    hits = acervo_catalog.query_catalog(mini_acervo, fts='"xenon marmalade protocol"')
    assert [r["path"] for r in hits] == ["micro/alpha/knowledge/coffee-preference.md"]


def test_doctor_finds_exactly_the_planted_problems(mini_acervo: Path) -> None:
    acervo_catalog.build_catalog(mini_acervo)
    report = acervo_catalog.doctor(mini_acervo)
    found = {(f["severity"], f["check"], f["path"]) for f in report["findings"]}
    assert found == {
        ("ERROR", "broken-link", "micro/alpha/decisions/broken-relates.md"),
        ("ERROR", "V2-020", "micro/alpha/knowledge/wrong-home.md"),
        ("ERROR", "V2-030", "micro/beta/context/lonely-superseded.md"),
        ("WARN", "broken-wikilink", "micro/beta/knowledge/v1-legacy.md"),
    }
    assert report["ok"] is False
    assert report["errors"] == 3
    assert report["warnings"] == 1


def test_doctor_detects_drift(mini_acervo: Path) -> None:
    acervo_catalog.build_catalog(mini_acervo)
    extra = mini_acervo / "micro/beta/knowledge/new-note.md"
    extra.write_text(_v02("knowledge", "New note", "Added after build"), encoding="utf-8")
    report = acervo_catalog.doctor(mini_acervo)
    assert ("WARN", "drift-extra", "micro/beta/knowledge/new-note.md") in {
        (f["severity"], f["check"], f["path"]) for f in report["findings"]
    }


def test_upsert_single_file(mini_acervo: Path) -> None:
    acervo_catalog.build_catalog(mini_acervo)
    target = mini_acervo / "micro/beta/knowledge/v1-legacy.md"
    target.write_text(
        target.read_text(encoding="utf-8").replace("Legacy v1 note", "Legacy v1 note renamed"),
        encoding="utf-8",
    )
    result = acervo_catalog.upsert_file(mini_acervo, target)
    assert result["action"] == "upserted"
    rows = acervo_catalog.query_catalog(mini_acervo, microverso="beta", type_="knowledge")
    assert rows[0]["title"] == "Legacy v1 note renamed"
    # removal path: delete file, upsert removes the row
    target.unlink()
    assert acervo_catalog.upsert_file(mini_acervo, target)["action"] == "removed"
    assert acervo_catalog.query_catalog(mini_acervo, microverso="beta", type_="knowledge") == []


def test_stats(mini_acervo: Path) -> None:
    acervo_catalog.build_catalog(mini_acervo)
    stats = acervo_catalog.stats_catalog(mini_acervo)
    assert stats["objects"] == EXPECTED_OBJECTS
    assert stats["by_layer"] == {"global": 1, "micro": 8}
    assert stats["by_status"]["superseded"] == 2
    assert stats["by_type"]["decision"] == 3  # incl. the wrong-home one


def _run_acervoctl(*argv: str) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(ACERVOCTL), *argv],
        capture_output=True, text=True, cwd=str(REPO / "scripts"),
    )
    return proc.returncode, json.loads(proc.stdout)


def test_acervoctl_reindex_and_doctor(mini_acervo: Path) -> None:
    code, payload = _run_acervoctl("reindex", "--acervo-root", str(mini_acervo))
    assert code == 0
    assert payload["ok"] is True
    assert payload["catalog_build"]["objects"] == EXPECTED_OBJECTS

    code, report = _run_acervoctl("doctor", "--acervo-root", str(mini_acervo))
    assert code == 1  # planted ERROR findings
    assert report["ok"] is False
    assert report["errors"] == 3
