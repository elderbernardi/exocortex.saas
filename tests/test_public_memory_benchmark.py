from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from lib.public_memory_benchmark import (  # noqa: E402
    audit_sample, cohens_kappa, holm_bonferroni, load_acervo_native, load_longmemeval,
    paired_bootstrap, retrieval_metrics, stratified_split, zero_event_upper_95,
)

CLI = SCRIPTS / "run_public_memory_benchmark.py"
ADAPTER = SCRIPTS / "acervo_public_benchmark_adapter.py"
NATIVE_GENERATOR = SCRIPTS / "generate_acervo_native_benchmark.py"


def lme_item(index: int, ability: str = "single-session-user") -> dict:
    qid = f"q-{index}"
    return {
        "question_id": qid,
        "question_type": ability,
        "question": f"What is marker{index}?",
        "answer": f"answer{index}",
        "question_date": "2026-01-02",
        "haystack_session_ids": [f"noise-{index}", f"evidence-{index}"],
        "haystack_dates": ["2025-01-01", "2025-01-02"],
        "haystack_sessions": [
            [{"role": "user", "content": "irrelevant material"}],
            [{"role": "user", "content": f"marker{index} is answer{index}", "has_answer": True}],
        ],
        "answer_session_ids": [f"evidence-{index}"],
    }


def run_cli(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args], cwd=REPO, text=True,
        capture_output=True, check=check,
    )


def test_load_longmemeval_and_stratified_split(tmp_path: Path) -> None:
    types = [
        "single-session-user", "multi-session", "knowledge-update", "temporal-reasoning",
    ]
    raw = [lme_item(i, types[i % 4]) for i in range(20)]
    for i in range(4):
        raw.append({**lme_item(100 + i), "question_id": f"q-{100+i}_abs"})
    source = tmp_path / "lme.json"
    source.write_text(json.dumps(raw), encoding="utf-8")
    cases, gold = load_longmemeval(source)
    split_a = stratified_split(cases, 10, 7)
    split_b = stratified_split(cases, 10, 7)
    assert split_a == split_b
    assert sum(value == "pilot" for value in split_a.values()) == 10
    assert len(gold) == len(cases) == 24
    assert any(case["ability"] == "abstention" for case in cases)


def test_prepare_separates_gold_and_hashes_artifacts(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    source.write_text(json.dumps([lme_item(i) for i in range(6)]), encoding="utf-8")
    workspace = tmp_path / "workspace"
    run_cli("prepare", "--dataset", "longmemeval-s", "--source", str(source),
            "--workspace", str(workspace), "--pilot-size", "2")
    query_text = (workspace / "prepared" / "queries.jsonl").read_text()
    ingest_text = (workspace / "prepared" / "ingest.jsonl").read_text()
    gold_text = (workspace / "sealed" / "gold.jsonl").read_text()
    assert '"answer"' not in query_text
    assert '"answer"' not in ingest_text
    assert '"answer"' in gold_text
    manifest = json.loads((workspace / "manifest.json").read_text())
    assert manifest["pilot_size"] == 2
    assert len(manifest["artifact_sha256"]) == 4


def test_retrieval_statistics_and_audit_are_deterministic() -> None:
    assert retrieval_metrics(["b", "a"], ["a"], 5) == {
        "recall_at_k": 1.0, "precision_at_k": 0.5, "mrr": 0.5,
    }
    a = [{"case_id": str(i), "score": float(i % 2)} for i in range(20)]
    b = [{"case_id": str(i), "score": 0.0} for i in range(20)]
    result = paired_bootstrap(a, b, "score", iterations=500, seed=3)
    assert result["effect"] == 0.5
    assert result["ci95"][0] >= 0
    assert zero_event_upper_95(400) == pytest.approx(0.007461, abs=1e-6)
    assert cohens_kappa([True, True, False, False], [True, True, False, False]) == 1.0
    assert holm_bonferroni({"a": 0.01, "b": 0.04})["a"]["reject"] is True
    rows = [{"case_id": str(i), "ability": f"g{i % 2}"} for i in range(100)]
    assert audit_sample(rows, 0.1, 9) == audit_sample(rows, 0.1, 9)
    assert len(audit_sample(rows, 0.1, 9)) == 10


def test_builtin_oracle_run_scores_perfect_retrieval(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    source.write_text(json.dumps([lme_item(i) for i in range(4)]), encoding="utf-8")
    workspace = tmp_path / "workspace"
    run_cli("prepare", "--dataset", "longmemeval-s", "--source", str(source),
            "--workspace", str(workspace), "--pilot-size", "2")
    run_cli("run", "--condition", "oracle", "--split", "pilot", "--workspace", str(workspace))
    evaluated = run_cli("evaluate", "--conditions", "oracle", "--split", "pilot",
                        "--workspace", str(workspace), "--bootstrap", "100", "--randomizations", "100")
    payload = json.loads(evaluated.stdout)
    assert payload["conditions"]["oracle"]["recall_at_5"] == 1.0
    assert payload["conditions"]["oracle"]["qa_accuracy"] is None
    assert payload["interpretation"] == "descriptive-only"


def test_acervo_adapter_is_disposable_and_retrieves_evidence() -> None:
    request = {
        "condition": "no-consolidation", "case_id": "case-1", "question": "What is zephyrcode?",
        "top_k": 5, "sessions": [
            {"session_id": "noise", "date": "2026-01-01", "turns": [{"role": "user", "content": "ordinary words only"}]},
            {"session_id": "answer", "date": "2026-01-02", "turns": [{"role": "user", "content": "zephyrcode is violet-seven"}]},
        ],
    }
    proc = subprocess.run(
        [sys.executable, str(ADAPTER)], cwd=REPO, input=json.dumps(request),
        text=True, capture_output=True, check=True,
    )
    response = json.loads(proc.stdout)
    assert "answer" in response["retrieved_session_ids"]
    assert response["adapter_root_policy"] == "deleted-after-response"


def test_full_run_requires_named_consolidator(tmp_path: Path) -> None:
    result = run_cli("run", "--condition", "full", "--workspace", str(tmp_path),
                     "--adapter-command", "true", check=False)
    assert result.returncode != 0
    assert "consolidator-id" in result.stderr


def test_native_suite_has_preregistered_counts_and_sealed_forbidden_ids(tmp_path: Path) -> None:
    source = tmp_path / "native.json"
    subprocess.run([sys.executable, str(NATIVE_GENERATOR), "--output", str(source)], check=True)
    raw = json.loads(source.read_text())
    assert raw["counts"]["cross_scope_trap"] == 400
    assert len(raw["cases"]) == 800
    cases, gold = load_acervo_native(source)
    assert len(cases) == len(gold) == 800
    trap = next(row for row in gold if row["case_id"] == "isolation-0000")
    assert trap["forbidden_session_ids"] == ["forbidden-0000"]


def test_official_judge_import_is_separate_from_raw_receipts(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    source.write_text(json.dumps([lme_item(1)]), encoding="utf-8")
    workspace = tmp_path / "workspace"
    run_cli("prepare", "--dataset", "longmemeval-s", "--source", str(source),
            "--workspace", str(workspace), "--pilot-size", "1")
    run_cli("run", "--condition", "oracle", "--split", "pilot", "--workspace", str(workspace))
    raw_path = workspace / "runs" / "oracle" / "pilot" / "repeat-1.jsonl"
    before = raw_path.read_bytes()
    judge = tmp_path / "judge.jsonl"
    judge.write_text(json.dumps({"question_id": "q-1", "autoeval_label": True}) + "\n")
    run_cli("import-judge", "--input", str(judge), "--condition", "oracle", "--split", "pilot",
            "--judge-id", "official-test", "--workspace", str(workspace))
    assert raw_path.read_bytes() == before
    evaluated = run_cli("evaluate", "--conditions", "oracle", "--split", "pilot",
                        "--workspace", str(workspace), "--bootstrap", "20", "--randomizations", "20")
    assert json.loads(evaluated.stdout)["conditions"]["oracle"]["qa_accuracy"] == 1.0
