"""Phase 4 write-side — entity refresh (04 §4.3) and episode distillation with
the H9 significance gate (04 §4.1, 07 §3)."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
TOOLS = REPO / "acervo" / "global" / "tools"
FIXTURE = REPO / "tests" / "memory-eval" / "fixture" / "acervo"

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(TOOLS))

import acervo_catalog  # noqa: E402
import acervo_semantic_core as core  # noqa: E402


@pytest.fixture()
def acervo(tmp_path: Path) -> Path:
    root = tmp_path / "acervo"
    shutil.copytree(FIXTURE, root)
    acervo_catalog.build_catalog(root)
    return root


@pytest.fixture()
def entity(acervo: Path) -> Path:
    out = core.new_object(
        acervo_root=acervo, type_="entity", scope="global",
        title="GPQ Logística", aliases=["gpq", "GPQ Log"], description="cliente")
    return Path(out["target_path"])


# ------------------------------------------------------------- refresh_entity

def test_refresh_entity_accrues_mention(acervo: Path, entity: Path) -> None:
    out = core.refresh_entity(
        acervo_root=acervo, path=entity, note="reunião de renovação",
        date="2026-07-08", add_aliases=["GPQ Transportes"])
    assert out["ok"] and out["last_interaction"] == "2026-07-08"
    text = entity.read_text(encoding="utf-8")
    assert "last_interaction: 2026-07-08" in text
    assert "GPQ Transportes" in text
    assert "- 2026-07-08 — reunião de renovação" in text
    # Interaction line sits under the append-only section, profile untouched.
    assert "## Perfil" in text and "## Interações" in text
    log = (acervo / "shared" / "_meta" / "log.md").read_text(encoding="utf-8")
    assert "UPDATED: shared/entities/gpq-logistica.md — entity refresh" in log


def test_refresh_entity_idempotent_bullet(acervo: Path, entity: Path) -> None:
    core.refresh_entity(acervo_root=acervo, path=entity, note="mesma nota", date="2026-07-08")
    core.refresh_entity(acervo_root=acervo, path=entity, note="mesma nota", date="2026-07-08")
    text = entity.read_text(encoding="utf-8")
    assert text.count("- 2026-07-08 — mesma nota") == 1


def test_refresh_entity_creates_section_when_absent(acervo: Path) -> None:
    # Entity built with a body that has no ## Interações section.
    out = core.new_object(
        acervo_root=acervo, type_="entity", scope="global", title="Sem Seção",
        aliases=["ss"], description="x", body="## Perfil\nsó perfil\n")
    ent = Path(out["target_path"])
    core.refresh_entity(acervo_root=acervo, path=ent, note="primeira", date="2026-07-08")
    text = ent.read_text(encoding="utf-8")
    assert "## Interações" in text and "- 2026-07-08 — primeira" in text


def test_refresh_entity_rejects_non_entity_and_empty_note(acervo: Path, entity: Path) -> None:
    with pytest.raises(RuntimeError, match="note é obrigatório"):
        core.refresh_entity(acervo_root=acervo, path=entity, note="  ")
    intent = core.new_object(
        acervo_root=acervo, type_="intention", scope="global",
        title="Uma intenção", due="2027-01-01")
    with pytest.raises(RuntimeError, match="não é uma entidade"):
        core.refresh_entity(acervo_root=acervo, path=Path(intent["target_path"]), note="x")


# --------------------------------------------------------- significance gate

def test_significance_gate_predicate() -> None:
    assert core.significance_gate(["decision"])["passed"] is True
    assert core.significance_gate([])["passed"] is False
    assert core.significance_gate(None)["passed"] is False
    g = core.significance_gate(["decision", "fofoca"])
    assert g["passed"] is True and g["unknown"] == ["fofoca"] and g["signals"] == ["decision"]


# ----------------------------------------------------------- distill_episode

def test_distill_episode_requires_signal(acervo: Path) -> None:
    with pytest.raises(RuntimeError, match="gate de significância H9"):
        core.distill_episode(acervo_root=acervo, scope="global", title="Papo",
                             summary="sem nada", signals=[])


def test_distill_episode_rejects_unknown_signal(acervo: Path) -> None:
    with pytest.raises(RuntimeError, match="signal desconhecido"):
        core.distill_episode(acervo_root=acervo, scope="global", title="X",
                             summary="y", signals=["boato"])


def test_distill_episode_requires_summary(acervo: Path) -> None:
    with pytest.raises(RuntimeError, match="summary é obrigatório"):
        core.distill_episode(acervo_root=acervo, scope="global", title="X",
                             summary="   ", signals=["decision"])


def test_distill_episode_creates_structured_episode(acervo: Path) -> None:
    out = core.distill_episode(
        acervo_root=acervo, scope="global", title="Fechamento GPQ",
        summary="Sessão fechou proposta e entregou artefato.",
        signals=["decision", "artifact"], participants=["gpq"],
        decisions=["Preço R$ 48k", "Início agosto"],
        open_loops=["Aguardando assinatura"],
        session_ref="session://tg-2026-07-08#dec-1")
    assert out["ok"] and out["operation"] == "distill_episode"
    assert out["significance"] == ["decision", "artifact"]
    text = Path(out["target_path"]).read_text(encoding="utf-8")
    assert "type: episode" in text and "class: perene" in text
    assert "entities: [gpq]" in text
    assert "## Decisões" in text and "- Preço R$ 48k" in text
    assert "## Loops abertos" in text and "## Sessão" in text
    assert "session://tg-2026-07-08#dec-1" in text
