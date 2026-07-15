"""Tests for acervo/global/tools/acervo_retrieve.py (Phase 3 hybrid retrieval).

Runs against a workdir copy of the memory-eval fixture acervo
(tests/memory-eval/fixture/) with catalog.sqlite built over the copy —
no derived state ever lands inside the fixture. Hindsight is never touched
(with_hindsight defaults to OFF per H2).
"""
from __future__ import annotations

import shutil
import sys
from datetime import date
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOLS = REPO / "acervo" / "global" / "tools"
FIXTURE_ACERVO = REPO / "tests" / "memory-eval" / "fixture" / "acervo"

sys.path.insert(0, str(TOOLS))

import acervo_catalog  # noqa: E402
import acervo_retrieve  # noqa: E402

TODAY = date(2026, 7, 4)  # the fixture's "present" (golden set assumes it)

RESTRICTED_NORTE = "micro/cliente-norte/knowledge/preco-frete-contratado.md"
RESTRICTED_SUL = "micro/expansao-sul/knowledge/preco-frete-corredor-sul.md"


@pytest.fixture(scope="module")
def acervo(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("retrieve") / "acervo"
    shutil.copytree(FIXTURE_ACERVO, root)
    acervo_catalog.build_catalog(root)
    return root


@pytest.fixture(scope="module")
def retriever(acervo: Path) -> acervo_retrieve.Retriever:
    return acervo_retrieve.Retriever(acervo, today=TODAY)


# ---------------------------------------------------------------- routing

@pytest.mark.parametrize(
    ("query", "route"),
    [
        ("Encontre onde aparece o termo exato 'posição-palete'.", "literal"),
        ("Qual era a taxa de armazenagem em março de 2026?", "temporal"),
        ("O que prometemos ao Ricardo e qual é a situação do prazo?", "prospective"),
        ("O seguro da frota foi renovado?", "prospective"),  # completion question
        ("Quem é o Ricardo e como ele prefere se comunicar?", "entity"),
        ("Onde paramos no projeto Expansão Sul?", "continuity"),
        ("Como fazer a homologação de uma transportadora?", "procedural"),
        ("Qual é o custo referencial por km da frota própria hoje?", "factual"),
    ],
)
def test_classify_query_routes(retriever: acervo_retrieve.Retriever, query: str, route: str) -> None:
    assert acervo_retrieve.classify_query(query, aliases=retriever.aliases) == route


def test_classify_alias_hit_is_entity(retriever: acervo_retrieve.Retriever) -> None:
    # "Norte" is an alias of the norte-mineracao entity (shared/entities)
    query = "Qual é o preço do frete contratado com a Norte Mineração?"
    assert acervo_retrieve.classify_query(query, aliases=retriever.aliases) == "entity"


def test_classify_rationale_beats_completion_pattern(retriever: acervo_retrieve.Retriever) -> None:
    # "foi escolhido?" looks like a completion question, but "por que" asks
    # for rationale → factual, not prospective.
    query = "Por que o corredor sul foi escolhido como a expansão de 2026?"
    assert acervo_retrieve.classify_query(query, aliases=retriever.aliases) == "factual"


def test_classify_hints_override(retriever: acervo_retrieve.Retriever) -> None:
    assert acervo_retrieve.classify_query("qualquer texto", hints={"route": "semantic"}) == "semantic"


# ---------------------------------------------------------------- scope guard

def test_restricted_never_leaves_home_scope(retriever: acervo_retrieve.Retriever) -> None:
    # cross_scope_trap: asked from expansao-sul, the cliente-norte price
    # (sensitivity: restricted) must never surface — not in paths, not in text.
    result = retriever.retrieve(
        "Para calibrar o preço-alvo do corredor sul, quanto cobramos hoje da Norte Mineração?",
        scope="expansao-sul",
    )
    paths = [item["path"] for item in result["items"] + result["view"]]
    assert RESTRICTED_NORTE not in paths
    packed_text = "".join(item.get("content") or "" for item in result["items"])
    assert "47,20" not in packed_text
    # the governing contract is the right answer surface
    assert "global/contracts/politica-confidencialidade-precos.md" in paths


def test_restricted_blocked_even_with_allow_scopes(retriever: acervo_retrieve.Retriever) -> None:
    result = retriever.retrieve(
        "Qual é o preço do frete contratado com a Norte Mineração?",
        scope="expansao-sul",
        allow_scopes=["cliente-norte"],
    )
    paths = [item["path"] for item in result["items"] + result["view"]]
    assert RESTRICTED_NORTE not in paths  # allow_scopes never unlocks restricted
    # but non-restricted cliente-norte objects become visible cross-scope
    assert any(p.startswith("micro/cliente-norte/") for p in paths)


def test_restricted_allowed_in_home_scope(retriever: acervo_retrieve.Retriever) -> None:
    result = retriever.retrieve(
        "Qual é o preço do frete contratado com a Norte Mineração?",
        scope="cliente-norte",
    )
    paths = [item["path"] for item in result["items"]]
    assert RESTRICTED_NORTE in paths
    assert RESTRICTED_SUL not in paths  # the other scope's restricted price


# ---------------------------------------------------------------- packing

def test_pack_budget_degrades_to_stubs(retriever: acervo_retrieve.Retriever) -> None:
    generous = retriever.retrieve(
        "O que a vistoria concluiu sobre a capacidade do armazém de Itajaí?",
        scope="expansao-sul",
    )
    assert generous["found"] and not any(it["stub"] for it in generous["items"])

    budget = 200
    tight = retriever.retrieve(
        "O que a vistoria concluiu sobre a capacidade do armazém de Itajaí?",
        scope="expansao-sul",
        budget_tokens=budget,
    )
    assert tight["found"]
    assert tight["total_tokens"] <= budget  # never exceed (07 §4)
    stubs = [it for it in tight["items"] + tight["view"] if it["stub"]]
    assert stubs, "budget overflow must degrade items to pointer stubs"
    for stub in stubs:
        assert stub["content"] is None
        assert stub["header"]  # pointer stub keeps header + description
    # best-ranked item survives as full content while any stub exists
    assert tight["items"][0]["stub"] is False or all(it["stub"] for it in tight["items"])


def test_pack_u_curve_order() -> None:
    def item(path: str, score: float) -> dict:
        return {
            "path": path, "role": "result", "header": f"[k] {path}", "content": "x" * 40,
            "description": "d", "score": score, "source": "t", "stub": False, "tokens_est": 11,
        }

    items = [item(f"f{i}.md", 10.0 - i) for i in range(4)]
    packed, _ = acervo_retrieve.pack(items, budget_tokens=10_000)
    # U-curve: best first, second-best last (lost-in-the-middle)
    assert [it["path"] for it in packed] == ["f0.md", "f2.md", "f3.md", "f1.md"]


# ---------------------------------------------------------------- abstention

def test_abstention_when_nothing_above_floor(retriever: acervo_retrieve.Retriever) -> None:
    result = retriever.retrieve(
        "Quanto pagamos de aluguel no armazém de Manaus?", scope="operacoes"
    )
    assert result["found"] is False
    assert result["items"] == [] and result["citations"] == []
    assert "não há registro no Acervo" in result["message"]


# ---------------------------------------------------------------- labeling

def test_dispute_banner_in_header(retriever: acervo_retrieve.Retriever) -> None:
    result = retriever.retrieve(
        "Qual é a capacidade útil do armazém de Itajaí medida na vistoria?",
        scope="operacoes",
    )
    disputed = {
        it["path"]: it["header"]
        for it in result["items"]
        if it["path"] == "micro/operacoes/knowledge/capacidade-util-armazem-itajai.md"
    }
    assert disputed, "the disputed measurement must surface in its home scope"
    header = disputed["micro/operacoes/knowledge/capacidade-util-armazem-itajai.md"]
    assert "DISPUTED" in header
    assert "conflito-capacidade-armazem-itajai" in header


def test_temporal_route_labels_historical(retriever: acervo_retrieve.Retriever) -> None:
    result = retriever.retrieve(
        "Quanto custava o km da frota em abril de 2026, antes da tabela atual?",
        scope="operacoes",
    )
    assert result["route"] == "temporal"
    assert result["as_of"] == "2026-04-15"
    v2 = [it for it in result["items"] if it["path"].endswith("tabela-frete-interna-v2.md")]
    assert v2 and "HISTORICAL" in v2[0]["header"]


def test_headers_and_citations_carry_paths(retriever: acervo_retrieve.Retriever) -> None:
    result = retriever.retrieve(
        "Qual é a taxa de armazenagem vigente hoje?", scope="operacoes"
    )
    assert result["found"]
    for item in result["items"]:
        assert item["path"] in item["header"]
        assert item["header"].startswith("[")  # [type|epistemic|confidence|status|scope]
    assert f"Acervo: {result['items'][0]['path']}" in result["citations"]
