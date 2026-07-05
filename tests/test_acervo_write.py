"""Phase 2 write-pipeline verbs (conflict-check / apply-supersede /
open-dispute / new-object) — 08-write-policy.md.

Each test builds an isolated acervo by copying the eval fixture into tmp_path
(never mutating the source fixture) and drives the acervo_semantic_core library
directly.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
FIXTURE = REPO / "tests" / "memory-eval" / "fixture" / "acervo"

import acervo_semantic_core as core  # noqa: E402


@pytest.fixture()
def acervo(tmp_path: Path) -> Path:
    root = tmp_path / "acervo"
    shutil.copytree(FIXTURE, root)
    catalog = core.load_tool_module(root, "acervo_catalog")
    catalog.build_catalog(root)
    return root


def _reindex(root: Path) -> None:
    core.load_tool_module(root, "acervo_catalog").build_catalog(root)


def _write(root: Path, rel: str, front: str, body: str = "Corpo.") -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"---\n{front}\n---\n{body}\n", encoding="utf-8")
    return p


_V02 = (
    "schema: acervo/v0.2\ntype: knowledge\ntitle: {title}\n"
    "description: {desc}\ntags: [{tags}]\ncreated_at: 2026-07-05T00:00:00Z\n"
    "class: volátil\nstatus: active\nepistemic: fact\nconfidence: high\n"
    "observed_at: 2026-07-05"
)


# ── conflict-check ───────────────────────────────────────────────────────────

def test_conflict_check_finds_planted_overlap(acervo: Path):
    price = acervo / "micro/expansao-sul/knowledge/preco-frete-corredor-sul.md"
    res = core.conflict_check(acervo_root=acervo, candidate_path=price)
    assert res["ok"] is True
    assert res["count"] >= 1
    # its own path is the exact-title enrich verdict
    self_hit = [o for o in res["overlaps"] if o["path"].endswith("preco-frete-corredor-sul.md")]
    assert self_hit and self_hit[0]["verdict"] == "enrich"


def test_conflict_check_no_llm_marker(acervo: Path):
    # deterministic: verdicts are limited to the documented set
    price = acervo / "micro/expansao-sul/knowledge/preco-frete-corredor-sul.md"
    res = core.conflict_check(acervo_root=acervo, candidate_path=price)
    assert all(o["verdict"] in {"enrich", "supersession", "overlap"} for o in res["overlaps"])


# ── apply-supersede ──────────────────────────────────────────────────────────

def test_apply_supersede_pairs_atomically(acervo: Path):
    k = acervo / "micro/operacoes/knowledge"
    new = _write(acervo, "micro/operacoes/knowledge/frete-v4.md",
                 _V02.format(title="Frete v4", desc="novo", tags="frete"))
    _reindex(acervo)
    old = k / "tabela-frete-interna-v3.md"
    res = core.apply_supersede(acervo_root=acervo, new_path=new, old_path=old)
    assert res["ok"] is True
    assert "status: superseded" in old.read_text(encoding="utf-8")
    assert "superseded_by:" in old.read_text(encoding="utf-8")
    assert "supersedes:" in new.read_text(encoding="utf-8")


def test_apply_supersede_refuses_perene_decision(acervo: Path):
    new = _write(acervo, "micro/cliente-norte/knowledge/x.md",
                 _V02.format(title="X", desc="d", tags="t"))
    _reindex(acervo)
    dec = next((acervo / "micro/cliente-norte/decisions").glob("*.md"))
    with pytest.raises(RuntimeError, match="cânone|canon|perene|imut"):
        core.apply_supersede(acervo_root=acervo, new_path=new, old_path=dec)


# ── open-dispute ─────────────────────────────────────────────────────────────

def test_open_dispute_creates_conflict_and_stamps_both(acervo: Path):
    a = _write(acervo, "micro/operacoes/knowledge/cap-a.md",
               _V02.format(title="Capacidade 12000", desc="A", tags="capacidade"))
    b = _write(acervo, "micro/operacoes/knowledge/cap-b.md",
               _V02.format(title="Capacidade 15000", desc="B", tags="capacidade"))
    _reindex(acervo)
    res = core.open_dispute(acervo_root=acervo, a_path=a, b_path=b,
                            title="Disputa de capacidade", scope="operacoes")
    assert res["ok"] is True
    conflict = acervo / res["relative_output"] if "relative_output" in res else None
    assert "disputed_by:" in a.read_text(encoding="utf-8")
    assert "disputed_by:" in b.read_text(encoding="utf-8")
    if conflict:
        assert "type: conflict" in conflict.read_text(encoding="utf-8")


# ── new-object ───────────────────────────────────────────────────────────────

def test_new_object_entity_requires_alias_and_dedups(acervo: Path):
    with pytest.raises(RuntimeError, match="aliases"):
        core.new_object(acervo_root=acervo, type_="entity", scope="operacoes",
                        title="Sem alias")
    # dup against an existing fixture entity alias
    existing = next((acervo / "shared/entities").glob("*.md"))
    import re
    aliases = re.search(r"aliases:\s*\[([^\]]+)\]", existing.read_text(encoding="utf-8"))
    if aliases:
        first = aliases.group(1).split(",")[0].strip().strip('"\'')
        with pytest.raises(RuntimeError, match="alias|existe|duplic"):
            core.new_object(acervo_root=acervo, type_="entity", scope="operacoes",
                            title="Colisão", aliases=[first])


def test_new_object_intention_requires_due_or_trigger(acervo: Path):
    with pytest.raises(RuntimeError, match="due|trigger|gatilho"):
        core.new_object(acervo_root=acervo, type_="intention", scope="operacoes",
                        title="Sem prazo")
    res = core.new_object(acervo_root=acervo, type_="intention", scope="operacoes",
                          title="Com prazo", due="2026-08-01")
    assert res["ok"] is True and res["status"] == "active"


def test_new_object_untrusted_forces_draft(acervo: Path):
    res = core.new_object(acervo_root=acervo, type_="intention", scope="operacoes",
                          title="Da web", due="2026-08-01", source_trust="untrusted")
    assert res["ok"] is True
    assert res["status"] == "draft"


def test_new_object_secret_refused(acervo: Path):
    with pytest.raises(RuntimeError, match="segredo|secret|V2-060"):
        core.new_object(acervo_root=acervo, type_="intention", scope="operacoes",
                        title="Vazamento", due="2026-08-01",
                        body="token: sk-abcdefghijklmnopqrstuvwxyz012345")


def test_created_files_pass_v2_validator(acervo: Path):
    res = core.new_object(acervo_root=acervo, type_="intention", scope="operacoes",
                          title="Valida", due="2026-08-01")
    validator = core.load_tool_module  # reuse module loader for scripts dir
    import subprocess
    out = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "validate_frontmatter.py"),
         "--file", str(acervo / res["relative_output"])],
        capture_output=True, text=True)
    assert out.returncode == 0, out.stdout + out.stderr
