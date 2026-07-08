"""Phase 4 read-only consolidation scan."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOLS = REPO / "acervo" / "global" / "tools"
ACERVOCTL = REPO / "scripts" / "acervoctl.py"
FIXTURE = REPO / "tests" / "memory-eval" / "fixture" / "acervo"

sys.path.insert(0, str(TOOLS))

import acervo_catalog  # noqa: E402
import acervo_consolidation  # noqa: E402


def _v02(type_: str, title: str, description: str, extra: str = "", status: str = "active", cls: str = "volátil") -> str:
    return (
        "---\n"
        "schema: acervo/v0.2\n"
        f"type: {type_}\n"
        f"title: {title}\n"
        f"description: {description}\n"
        "tags: [test]\n"
        f"class: {cls}\n"
        f"status: {status}\n"
        "created_at: 2026-01-01T00:00:00Z\n"
        f"{extra}"
        "---\n\n"
        f"# {title}\n"
    )


@pytest.fixture()
def acervo(tmp_path: Path) -> Path:
    root = tmp_path / "acervo"
    shutil.copytree(FIXTURE, root)
    base = root / "micro" / "operacoes"

    (base / "intentions").mkdir(exist_ok=True)
    (base / "intentions" / "vencida.md").write_text(
        _v02("intention", "Intenção vencida", "Deve aparecer", "due: 2026-07-01\n"),
        encoding="utf-8",
    )
    (base / "intentions" / "proxima.md").write_text(
        _v02("intention", "Intenção próxima", "Deve aparecer", "due: 2026-07-08\n"),
        encoding="utf-8",
    )
    (base / "knowledge" / "review-due.md").write_text(
        _v02("knowledge", "Revisar preço", "Review vencido", "review_after: 2026-07-01\nlast_accessed_at: 2026-07-01T00:00:00Z\n"),
        encoding="utf-8",
    )
    (base / "knowledge" / "stale.md").write_text(
        _v02("knowledge", "Volátil antigo", "Inativo", "last_accessed_at: 2026-01-01T00:00:00Z\n"),
        encoding="utf-8",
    )
    (base / "knowledge" / "draft.md").write_text(
        _v02("knowledge", "Rascunho", "Trust gate", status="draft"),
        encoding="utf-8",
    )
    (base / "knowledge" / "conflict.md").write_text(
        _v02("conflict", "Conflito aberto", "Disputa", cls="perene"),
        encoding="utf-8",
    )
    acervo_catalog.build_catalog(root)
    return root


def test_consolidation_scan_buckets(acervo: Path) -> None:
    payload = acervo_consolidation.scan(acervo, today="2026-07-04", stale_days=90, upcoming_days=7)
    assert payload["ok"] is True
    assert payload["counts"]["intentions_due"] >= 1
    assert payload["counts"]["intentions_upcoming"] >= 1
    assert payload["counts"]["review_due"] >= 1
    assert payload["counts"]["stale_volatile"] >= 1
    assert payload["counts"]["drafts"] >= 1
    assert payload["counts"]["open_disputes"] >= 1

    assert any(item["path"].endswith("vencida.md") for item in payload["buckets"]["intentions_due"])
    assert any(item["path"].endswith("proxima.md") for item in payload["buckets"]["intentions_upcoming"])


def test_markdown_renderer_mentions_actions(acervo: Path) -> None:
    payload = acervo_consolidation.scan(acervo, today="2026-07-04")
    md = acervo_consolidation.render_markdown(payload)
    assert "# Acervo Consolidation Scan" in md
    assert "intentions_due" in md
    assert "Next actions" in md


def test_backup_dirs_excluded_from_dedup(acervo: Path) -> None:
    # A backup snapshot carrying the same title as a live file must NOT surface as
    # a dedup candidate — _backup is a lifecycle dir (SKIP_PARTS), not active memory.
    base = acervo / "micro" / "operacoes"
    (base / "knowledge" / "registro.md").write_text(
        _v02("knowledge", "Registro Duplicado", "vivo", cls="perene"), encoding="utf-8",
    )
    bak = base / "_backup" / "snap"
    bak.mkdir(parents=True, exist_ok=True)
    (bak / "registro.md").write_text(
        _v02("knowledge", "Registro Duplicado", "backup", cls="perene"), encoding="utf-8",
    )
    acervo_catalog.build_catalog(acervo)
    payload = acervo_consolidation.scan(acervo, today="2026-07-08")
    for item in payload["buckets"]["duplicate_titles"]:
        assert not any("_backup" in p for p in item.get("paths", [])), item


def test_acervoctl_consolidation_scan(acervo: Path) -> None:
    proc = subprocess.run(
        [sys.executable, str(ACERVOCTL), "consolidation-scan", "--acervo-root", str(acervo), "--today", "2026-07-04"],
        capture_output=True,
        text=True,
        cwd=str(REPO / "scripts"),
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["operation"] == "consolidation_scan"
    assert payload["counts"]["intentions_due"] >= 1
