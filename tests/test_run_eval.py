"""Smoke test for tests/memory-eval/run_eval.py (H2 retrieval-eval harness).

Catalog strategy only — Hindsight is deliberately skipped in unit tests.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
RUN_EVAL = REPO / "tests" / "memory-eval" / "run_eval.py"

SMOKE_IDS = ["G01", "G08", "G23"]  # factual, temporal, absent


@pytest.fixture(scope="module")
def run_eval_mod():
    spec = importlib.util.spec_from_file_location("run_eval", RUN_EVAL)
    module = importlib.util.module_from_spec(spec)
    sys.modules["run_eval"] = module
    spec.loader.exec_module(module)
    return module


def test_catalog_smoke_end_to_end(run_eval_mod, tmp_path: Path) -> None:
    m = run_eval_mod
    acervo = m.build_workdir_catalog(tmp_path)
    assert (acervo / "global/tools/state/catalog.sqlite").exists()
    # catalog stays in the workdir copy, never inside the fixture
    assert not (m.FIXTURE_ACERVO / "global/tools").exists()

    corpus = m.Corpus(acervo)
    questions = [q for q in m.load_questions() if q.id in SMOKE_IDS]
    assert [q.id for q in questions] == SMOKE_IDS

    results = m.run_eval(questions, {"catalog": m.CatalogStrategy(acervo, corpus)}, corpus)
    overall = results["strategies"]["catalog"]["overall"]
    assert overall["n"] == len(SMOKE_IDS)
    assert 0.0 <= overall["recall"] <= 1.0
    assert 0.0 <= overall["precision"] <= 1.0
    assert 0.0 <= overall["contamination_rate"] <= 1.0
    assert overall["abstention_accuracy"] in (0.0, 1.0)  # single absent question
    assert overall["avg_token_cost"] >= 0

    rows = {r["id"]: r for r in results["strategies"]["catalog"]["questions"]}
    # G01: the planted fact must surface without leaking the other scope's price
    assert rows["G01"]["recall"] == 1.0
    assert rows["G01"]["contaminated"] is False
    # G08: temporal question resolves the Q1 validity window
    assert "acervo/micro/operacoes/knowledge/taxa-armazenagem-q1.md" in rows["G08"]["top"]
    # G23: abstention question carries a boolean abstention verdict, no recall
    assert rows["G23"]["recall"] is None
    assert rows["G23"]["abstention_correct"] in (True, False)


def test_scope_filter_blocks_cross_scope(run_eval_mod, tmp_path: Path) -> None:
    m = run_eval_mod
    assert m.allowed_prefixes("cliente-norte") == ("micro/cliente-norte/", "shared/", "global/")
    assert m.allowed_prefixes("global") == ("global/", "shared/")


def test_query_helpers(run_eval_mod) -> None:
    m = run_eval_mod
    assert "posicao-palete" in m.query_terms("o termo exato 'posição-palete'")
    assert m.query_date("Qual era a taxa em março de 2026?") == "2026-03-15"
    assert m.query_date("taxa vigente hoje") is not None
    assert m.query_date("Qual é o preço do frete?") is None
