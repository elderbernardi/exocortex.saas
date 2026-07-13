"""Smoke test for tests/memory-eval/run_eval.py (H2 retrieval-eval harness).

Catalog strategy only — Hindsight is deliberately skipped in unit tests.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
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


def test_build_workdir_acervo_accepts_custom_source(run_eval_mod, tmp_path: Path) -> None:
    m = run_eval_mod
    source = tmp_path / "live-acervo"
    shutil.copytree(m.FIXTURE_ACERVO, source)
    workdir = tmp_path / "workdir"

    copied = m.build_workdir_acervo(source, workdir)

    assert copied == workdir / "acervo"
    assert (copied / "global/tools/state/catalog.sqlite").exists()
    # source root stays untouched — no derived state is written back into the live tree
    assert not (source / "global/tools").exists()


def test_score_question_reads_custom_corpus_not_fixture(run_eval_mod, tmp_path: Path) -> None:
    m = run_eval_mod
    source = tmp_path / "live-acervo"
    shutil.copytree(m.FIXTURE_ACERVO, source)
    live_doc = source / "micro" / "live-scope" / "knowledge" / "live-only.md"
    live_doc.parent.mkdir(parents=True, exist_ok=True)
    live_doc.write_text(
        "---\n"
        "schema: acervo/v0.2\n"
        "type: knowledge\n"
        "title: Live only retrieval target\n"
        "description: unique live-only retrieval document\n"
        "class: volátil\n"
        "status: active\n"
        "epistemic: fact\n"
        "created_at: 2026-07-12T00:00:00Z\n"
        "---\n\n"
        "Purple narwhal ledger for live evaluation only.\n",
        encoding="utf-8",
    )
    acervo = m.build_workdir_acervo(source, tmp_path / "workdir-live")
    corpus = m.Corpus(acervo)
    q = m.Question(
        id="LIV01",
        category="factual",
        scope="live-scope",
        query="purple narwhal ledger",
        expected_paths=["acervo/micro/live-scope/knowledge/live-only.md"],
        forbidden_paths=[],
        forbidden_content=[],
        expected_answer_fragments=["narwhal"],
        expects_abstention=False,
    )

    results = m.run_eval([q], {"catalog": m.CatalogStrategy(acervo, corpus)}, corpus)
    row = results["strategies"]["catalog"]["questions"][0]
    assert row["top"][0] == "acervo/micro/live-scope/knowledge/live-only.md"
    assert row["recall"] == 1.0


def test_query_helpers(run_eval_mod) -> None:
    m = run_eval_mod
    assert "posicao-palete" in m.query_terms("o termo exato 'posição-palete'")
    assert m.query_date("Qual era a taxa em março de 2026?") == "2026-03-15"
    assert m.query_date("taxa vigente hoje") is not None
    assert m.query_date("Qual é o preço do frete?") is None


# --- CI regression gate (10-evaluation.md §4) --------------------------------

BASELINE_METRICS = {
    "recall": 0.80, "precision": 0.35,
    "abstention_accuracy": 0.33, "contamination_rate": 0.0,
}


def _baseline(**overrides):
    metrics = {**BASELINE_METRICS, **overrides}
    return {"strategy": "catalog", "metrics": metrics}


def test_gate_passes_when_unchanged(run_eval_mod) -> None:
    m = run_eval_mod
    rows = m.compare_to_baseline(dict(BASELINE_METRICS), _baseline())
    assert not any(r["blocked"] for r in rows)


def test_gate_passes_on_improvement(run_eval_mod) -> None:
    m = run_eval_mod
    # recall up, precision up — improvements never block
    current = {**BASELINE_METRICS, "recall": 0.95, "precision": 0.60}
    rows = m.compare_to_baseline(current, _baseline())
    assert not any(r["blocked"] for r in rows)


def test_gate_tolerates_small_regression(run_eval_mod) -> None:
    m = run_eval_mod
    # 8-point recall drop is under the 10-point threshold → allowed
    current = {**BASELINE_METRICS, "recall": 0.72}
    rows = m.compare_to_baseline(current, _baseline())
    assert not any(r["blocked"] for r in rows)


def test_gate_blocks_recall_regression(run_eval_mod) -> None:
    m = run_eval_mod
    # 15-point recall drop → blocks
    current = {**BASELINE_METRICS, "recall": 0.65}
    rows = m.compare_to_baseline(current, _baseline())
    recall = next(r for r in rows if r["metric"] == "recall")
    assert recall["blocked"] is True
    assert recall["delta_pts"] == -15.0


def test_gate_blocks_any_contamination(run_eval_mod) -> None:
    m = run_eval_mod
    # contamination has a HARD ceiling of 0 — even a tiny leak blocks,
    # independent of the 10-point regression threshold
    current = {**BASELINE_METRICS, "contamination_rate": 0.04}
    rows = m.compare_to_baseline(current, _baseline())
    cont = next(r for r in rows if r["metric"] == "contamination_rate")
    assert cont["blocked"] is True


def test_gate_end_to_end_against_committed_baseline(run_eval_mod, tmp_path) -> None:
    m = run_eval_mod
    acervo = m.build_workdir_catalog(tmp_path)
    corpus = m.Corpus(acervo)
    questions = m.load_questions()
    current = m.gate_overall(acervo, corpus, questions)
    baseline = json.loads(m.BASELINE_PATH.read_text(encoding="utf-8"))
    rows = m.compare_to_baseline(current, baseline)
    # the committed baseline must match today's deterministic catalog run
    assert not any(r["blocked"] for r in rows), m.render_gate(rows)


def test_custom_report_identity_defaults(run_eval_mod, tmp_path: Path) -> None:
    m = run_eval_mod
    custom_questions = tmp_path / "questions.local.yaml"
    custom_questions.write_text(m.GOLDEN.read_text(encoding="utf-8"), encoding="utf-8")
    custom_acervo = tmp_path / "live-acervo"
    shutil.copytree(m.FIXTURE_ACERVO, custom_acervo)

    assert m.default_report_prefix(m.FIXTURE_ACERVO, m.GOLDEN) == "h2"
    assert m.default_report_prefix(custom_acervo, custom_questions) == "questions-local"
    assert m.default_report_title(custom_acervo, custom_questions, "2026-07-12").startswith("Memory eval —")


def test_gate_rejects_custom_inputs(run_eval_mod, tmp_path: Path) -> None:
    m = run_eval_mod
    custom_questions = tmp_path / "questions.local.yaml"
    custom_questions.write_text(m.GOLDEN.read_text(encoding="utf-8"), encoding="utf-8")
    custom_acervo = tmp_path / "live-acervo"
    shutil.copytree(m.FIXTURE_ACERVO, custom_acervo)

    rc = m.main([
        "--gate",
        "--acervo-root", str(custom_acervo),
        "--questions-file", str(custom_questions),
    ])

    assert rc == 2
