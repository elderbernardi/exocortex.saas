"""Static acceptance contract for Phase 7 natural-language agent routing."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_briefing_skill_routes_to_v2_control_plane() -> None:
    text = (REPO / "skills/excrtx-behavior-briefing/SKILL.md").read_text(encoding="utf-8")
    assert "version: 2.0.0" in text
    assert 'acervoctl.py" briefing' in text
    assert "intentions/" in text
    assert "episodes/" in text
    assert "calendar_status:not_configured" in text
    assert "≤4k tokens" in text


def test_memory_manager_routes_decision_research_and_temporal_phrases() -> None:
    text = (REPO / "skills/excrtx-memory-manager/SKILL.md").read_text(encoding="utf-8")
    assert "version: 3.1.0" in text
    assert "--mode decision" in text
    assert "--mode research" in text
    assert "o que acreditávamos" in text
    assert "HISTORICAL" in text
    assert "o executivo decide" in text
    assert "Reads are physically read-only" in text
    assert "No canonical file changed as a side effect of READ" in text


def test_executive_guide_covers_trust_contract() -> None:
    text = (REPO / "docs/guides/como-funciona-sua-memoria.md").read_text(encoding="utf-8")
    for phrase in (
        "Briefing", "Modo decisão", "Modo pesquisa", "não há registro no Acervo",
        "Acervo: caminho/do/arquivo.md",
    ):
        assert phrase in text
