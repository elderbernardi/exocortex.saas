"""Phase 7 human-interface tests: briefing v2 and decision/research postures."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOLS = REPO / "acervo" / "global" / "tools"
FIXTURE = REPO / "tests" / "memory-eval" / "fixture" / "acervo"
CTL = REPO / "scripts" / "acervoctl.py"

sys.path.insert(0, str(TOOLS))

import acervo_catalog  # noqa: E402
import acervo_interface  # noqa: E402


@pytest.fixture()
def acervo(tmp_path: Path) -> Path:
    root = tmp_path / "acervo"
    shutil.copytree(FIXTURE, root)
    acervo_catalog.build_catalog(root)
    return root


def test_detailed_briefing_surfaces_governance_and_citations(acervo: Path) -> None:
    payload = acervo_interface.briefing(acervo, today="2026-07-04")

    assert payload["ok"] is True
    assert payload["tokens_est"] <= 4000
    assert payload["calendar_status"] == "not_configured"
    assert payload["sections"]["intentions_due"][0]["days_overdue"] == 4
    assert payload["sections"]["open_disputes"]
    assert "Ações vencidas" in payload["markdown"]
    assert "Disputas abertas" in payload["markdown"]
    assert any("intentions/" in citation for citation in payload["citations"])


def test_compact_briefing_is_at_most_ten_lines_and_scope_filtered(acervo: Path) -> None:
    payload = acervo_interface.briefing(
        acervo, today="2026-07-04", scopes=["cliente-norte"], compact=True
    )

    lines = payload["markdown"].splitlines()
    assert len(lines) <= 10
    assert "Enviar ao Ricardo" in payload["markdown"]
    assert "capacidade do armazém de Itajaí" not in payload["markdown"]


def test_briefing_joins_only_events_for_selected_day(acervo: Path, tmp_path: Path) -> None:
    calendar = tmp_path / "calendar.json"
    calendar.write_text(json.dumps({"events": [
        {"title": "Revisão executiva", "start": "2026-07-04T09:00:00Z"},
        {"title": "Outro dia", "start": "2026-07-05T09:00:00Z"},
    ]}), encoding="utf-8")

    payload = acervo_interface.briefing(
        acervo, today="2026-07-04", calendar_file=calendar
    )

    assert payload["calendar_status"] == "joined"
    assert [event["title"] for event in payload["sections"]["agenda"]] == ["Revisão executiva"]


def test_decision_posture_prefers_governing_types(acervo: Path) -> None:
    payload = acervo_interface.posture(
        acervo, mode="decision", scope="expansao-sul",
        query="galpão Itajaí compra locação decisão",
    )

    assert payload["found"] is True
    types = [item["header"].split("|", 1)[0].lstrip("[") for item in payload["items"]]
    assert "decision" in types
    assert all(item["path"].startswith(("micro/expansao-sul/", "shared/", "global/")) for item in payload["items"])
    assert payload["total_tokens"] <= payload["budget_tokens"]
    assert payload["citations"]


def test_research_posture_surfaces_tension_without_cross_scope_leak(acervo: Path) -> None:
    payload = acervo_interface.posture(
        acervo, mode="research", scope="expansao-sul",
        query="capacidade armazém Itajaí conflito",
    )

    paths = [item["path"] for item in payload["items"]]
    assert payload["found"] is True
    assert any("conflito-capacidade" in path for path in paths)
    assert not any(path.startswith("micro/cliente-norte/") for path in paths)
    assert "Não feche conclusão" in payload["instruction"]


@pytest.mark.parametrize(
    "args,operation",
    [
        (["briefing", "--today", "2026-07-04", "--mode", "compact"], "briefing"),
        (["posture", "--mode", "decision", "--scope", "expansao-sul",
          "--query", "galpão Itajaí compra locação decisão"], "posture"),
    ],
)
def test_acervoctl_phase7_commands(acervo: Path, args: list[str], operation: str) -> None:
    proc = subprocess.run(
        [sys.executable, str(CTL), *args, "--acervo-root", str(acervo)],
        text=True, capture_output=True, check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["operation"] == operation
