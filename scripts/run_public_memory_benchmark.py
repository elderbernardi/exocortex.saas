#!/usr/bin/env python3
"""Prepare, run, evaluate, and report Acervo public memory benchmarks.

The runner is adapter-driven: it never gives gold answers to the system under
test.  Long-context and oracle retrieval are built in; Acervo conditions use a
JSON stdin/stdout adapter so the exact deployed system can be pinned in the
protocol.  See tests/memory-eval/public/README.md for the protocol.
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

from lib.public_memory_benchmark import (  # noqa: E402
    CONDITIONS, LME_URL, LOCOMO_URL, DecisionThresholds, audit_sample,
    canonical_json, cohens_kappa, immutable_receipt, load_acervo_native, load_locomo,
    load_longmemeval, manifest_hashes, mean, paired_bootstrap,
    paired_randomization_test, percentile, read_jsonl, retrieval_metrics, sha256_file,
    stratified_split, utc_now, write_json, write_jsonl, zero_event_upper_95,
)

DEFAULT_WORKSPACE = REPO / "tests" / "memory-eval" / "public" / "workspace"
PROTOCOL_VERSION = "1.0"


def _download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".part")
    with urllib.request.urlopen(url, timeout=120) as response, partial.open("wb") as out:
        while chunk := response.read(1024 * 1024):
            out.write(chunk)
    partial.replace(destination)


def command_prepare(args: argparse.Namespace) -> int:
    workspace = args.workspace.resolve()
    default_names = {
        "longmemeval-s": "longmemeval_s_cleaned.json",
        "locomo": "locomo10.json",
        "acervo-native": "acervo-native.json",
    }
    source = args.source.resolve() if args.source else workspace / "source" / default_names[args.dataset]
    if not source.exists():
        if not args.download:
            raise SystemExit(f"source not found: {source}; pass --source or --download")
        if args.dataset == "acervo-native":
            raise SystemExit("acervo-native has no remote download; generate it and pass --source")
        _download(LME_URL if args.dataset == "longmemeval-s" else LOCOMO_URL, source)
    loader = {
        "longmemeval-s": load_longmemeval,
        "locomo": load_locomo,
        "acervo-native": load_acervo_native,
    }[args.dataset]
    cases, gold = loader(source)
    split = stratified_split(cases, args.pilot_size, args.seed) if args.dataset == "longmemeval-s" else {
        str(case["case_id"]): "replication" for case in cases
    }
    queries = []
    ingest = []
    gold_rows = []
    gold_by_id = {str(row["case_id"]): row for row in gold}
    for case in cases:
        case_id = str(case["case_id"])
        common = {
            "case_id": case_id, "cluster_id": case["cluster_id"],
            "ability": case["ability"], "question_type": case["question_type"],
            "split": split[case_id], "scope": case.get("scope"),
            "allow_scopes": case.get("allow_scopes", []),
        }
        ingest.append({**common, "sessions": case["sessions"]})
        queries.append({
            **common, "question": case["question"], "question_date": case["question_date"]
        })
        gold_rows.append({**common, **gold_by_id[case_id]})
    prepared = workspace / "prepared"
    sealed = workspace / "sealed"
    write_jsonl(prepared / "ingest.jsonl", ingest)
    write_jsonl(prepared / "queries.jsonl", queries)
    write_jsonl(sealed / "gold.jsonl", gold_rows)
    write_json(prepared / "split.json", {"seed": args.seed, "assignments": split})
    artifact_paths = [prepared / "ingest.jsonl", prepared / "queries.jsonl", prepared / "split.json", sealed / "gold.jsonl"]
    manifest = {
        "protocol_version": PROTOCOL_VERSION,
        "created_at": utc_now(),
        "dataset": args.dataset,
        "dataset_source": str(source),
        "dataset_url": LME_URL if args.dataset == "longmemeval-s" else (LOCOMO_URL if args.dataset == "locomo" else None),
        "dataset_sha256": sha256_file(source),
        "seed": args.seed,
        "pilot_size": sum(value == "pilot" for value in split.values()),
        "confirmatory_size": sum(value == "confirmatory" for value in split.values()),
        "n": len(cases),
        "artifact_sha256": manifest_hashes(artifact_paths, workspace),
        "gold_separation": "sealed/gold.jsonl is not passed to run adapters",
    }
    write_json(workspace / "manifest.json", manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


def _adapter(command: str, request: dict[str, Any], timeout: int) -> dict[str, Any]:
    proc = subprocess.run(
        shlex.split(command), input=canonical_json(request) + "\n", text=True,
        capture_output=True, timeout=timeout, env={**os.environ, "ACERVO_BENCHMARK_PROTOCOL": PROTOCOL_VERSION},
    )
    if proc.returncode:
        raise RuntimeError(f"adapter exited {proc.returncode}: {proc.stderr[-2000:]}")
    try:
        response = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"adapter returned invalid JSON: {proc.stdout[-2000:]}") from exc
    if not isinstance(response, dict):
        raise RuntimeError("adapter response must be a JSON object")
    return response


def _builtin_context(condition: str, sessions: list[dict[str, Any]], evidence: list[str] | None) -> dict[str, Any]:
    chosen = sessions if condition == "long-context" else [s for s in sessions if s["session_id"] in set(evidence or [])]
    return {
        "retrieved_session_ids": [s["session_id"] for s in chosen],
        "contexts": chosen,
        "retrieval": "all-history" if condition == "long-context" else "oracle-evidence",
    }


def _reader(command: str | None, request: dict[str, Any], timeout: int) -> dict[str, Any]:
    if not command:
        return {"hypothesis": None, "reader_status": "not-run"}
    response = _adapter(command, request, timeout)
    if "hypothesis" not in response:
        raise RuntimeError("reader response is missing hypothesis")
    return response


def command_run(args: argparse.Namespace) -> int:
    if args.condition not in ("long-context", "oracle") and not args.adapter_command:
        raise SystemExit("Acervo conditions require --adapter-command; no surrogate implementation is permitted")
    if args.condition == "full" and not args.consolidator_id:
        raise SystemExit("full requires --consolidator-id to identify the pinned consolidation implementation")
    workspace = args.workspace.resolve()
    ingest = {str(row["case_id"]): row for row in read_jsonl(workspace / "prepared" / "ingest.jsonl")}
    queries = read_jsonl(workspace / "prepared" / "queries.jsonl")
    # Oracle needs evidence locations, but never the expected answer.  This is
    # an explicit published baseline, not a system-under-test condition.
    oracle_evidence = {}
    if args.condition == "oracle":
        oracle_evidence = {
            str(row["case_id"]): row["evidence_session_ids"]
            for row in read_jsonl(workspace / "sealed" / "gold.jsonl")
        }
    selected = [q for q in queries if args.split == "all" or q["split"] == args.split]
    output = workspace / "runs" / args.condition / args.split / f"repeat-{args.repeat}.jsonl"
    rows = []
    for index, query in enumerate(selected, 1):
        case_id = str(query["case_id"])
        request = {
            "protocol_version": PROTOCOL_VERSION,
            "condition": args.condition,
            "repeat": args.repeat,
            "case_id": case_id,
            "cluster_id": query["cluster_id"],
            "ability": query["ability"],
            "question_type": query["question_type"],
            "question": query["question"],
            "question_date": query["question_date"],
            "scope": query.get("scope"),
            "allow_scopes": query.get("allow_scopes", []),
            "sessions": ingest[case_id]["sessions"],
            "top_k": args.top_k,
            "seed": args.seed + args.repeat,
            "consolidator_id": args.consolidator_id,
        }
        started = time.perf_counter()
        error = None
        try:
            if args.condition in ("long-context", "oracle"):
                result = _builtin_context(args.condition, request["sessions"], oracle_evidence.get(case_id))
            else:
                result = _adapter(args.adapter_command, request, args.timeout)
            reader_request = {
                "protocol_version": PROTOCOL_VERSION, "case_id": case_id,
                "question": query["question"], "question_date": query["question_date"],
                "contexts": result.get("contexts", []),
            }
            result.update(_reader(args.reader_command, reader_request, args.timeout))
        except Exception as exc:  # retain failures as immutable observations
            error = f"{type(exc).__name__}: {exc}"
            result = {"retrieved_session_ids": [], "contexts": [], "hypothesis": None}
        elapsed_ms = (time.perf_counter() - started) * 1000
        base = {
            "protocol_version": PROTOCOL_VERSION, "run_at": utc_now(),
            "condition": args.condition, "repeat": args.repeat, "split": query["split"],
            "case_id": case_id, "cluster_id": query["cluster_id"],
            "ability": query["ability"], "question_type": query["question_type"],
            "retrieved_session_ids": result.get("retrieved_session_ids", []),
            "hypothesis": result.get("hypothesis"), "judge_label": result.get("judge_label"),
            "latency_ms": result.get("latency_ms", elapsed_ms),
            "input_tokens": result.get("input_tokens"), "output_tokens": result.get("output_tokens"),
            "citation_correct": result.get("citation_correct"),
            "extracted_object_types": result.get("extracted_object_types", []),
            "contaminated": bool(result.get("contaminated", False)),
            "correction_required": result.get("correction_required"),
            "model_id": args.model_id, "judge_id": args.judge_id,
            "adapter_id": args.adapter_id, "consolidator_id": args.consolidator_id,
            "code_version": args.code_version, "error": error,
        }
        rows.append(immutable_receipt(base))
        if index % 25 == 0:
            print(f"completed {index}/{len(selected)}", file=sys.stderr)
    write_jsonl(output, rows)
    print(json.dumps({"output": str(output), "n": len(rows), "errors": sum(bool(r["error"]) for r in rows)}, indent=2))
    return 1 if any(r["error"] for r in rows) and args.fail_on_error else 0


def _load_condition(workspace: Path, condition: str, split: str) -> list[dict[str, Any]]:
    paths = sorted((workspace / "runs" / condition / split).glob("repeat-*.jsonl"))
    if not paths:
        return []
    rows = [row for path in paths for row in read_jsonl(path)]
    judgment_paths = sorted((workspace / "judgments" / condition / split).glob("repeat-*.jsonl"))
    judgments = {
        (str(row["case_id"]), int(row.get("repeat", 1))): row
        for path in judgment_paths for row in read_jsonl(path)
    }
    for row in rows:
        judged = judgments.get((str(row["case_id"]), int(row.get("repeat", 1))))
        if judged:
            row["judge_label"] = judged.get("judge_label")
            row["judge_id"] = judged.get("judge_id", row.get("judge_id"))
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["case_id"])].append(row)
    reduced = []
    for case_id, repeats in grouped.items():
        first = dict(repeats[0])
        for metric in ("latency_ms", "input_tokens", "output_tokens"):
            first[metric] = mean(r.get(metric) for r in repeats)
        labels = [r.get("judge_label") for r in repeats if r.get("judge_label") is not None]
        first["qa_accuracy"] = mean(float(bool(x)) for x in labels)
        first["contaminated"] = any(r.get("contaminated") for r in repeats)
        first["citation_fidelity"] = mean(float(bool(r["citation_correct"])) for r in repeats if r.get("citation_correct") is not None)
        first["correction_rate"] = mean(float(bool(r["correction_required"])) for r in repeats if r.get("correction_required") is not None)
        retrieved = [r.get("retrieved_session_ids", []) for r in repeats]
        first["retrieved_session_ids"] = retrieved[0] if retrieved else []
        reduced.append(first)
    return sorted(reduced, key=lambda r: str(r["case_id"]))


def command_export_qa(args: argparse.Namespace) -> int:
    workspace = args.workspace.resolve()
    source = workspace / "runs" / args.condition / args.split / f"repeat-{args.repeat}.jsonl"
    rows = read_jsonl(source)
    missing = [r["case_id"] for r in rows if r.get("hypothesis") is None]
    if missing:
        raise SystemExit(f"{len(missing)} rows have no hypothesis; run with --reader-command first")
    output = args.output.resolve() if args.output else workspace / "official" / args.condition / args.split / f"repeat-{args.repeat}-hypotheses.jsonl"
    write_jsonl(output, ({"question_id": r["case_id"], "hypothesis": r["hypothesis"]} for r in rows))
    print(json.dumps({"output": str(output), "n": len(rows)}, indent=2))
    return 0


def command_import_judge(args: argparse.Namespace) -> int:
    """Import the official LongMemEval evaluator JSONL without rewriting receipts."""
    workspace = args.workspace.resolve()
    labels = []
    for row in read_jsonl(args.input.resolve()):
        case_id = row.get("question_id", row.get("case_id"))
        label = row.get("autoeval_label", row.get("judge_label"))
        if case_id is None or label is None:
            raise SystemExit("judge rows require question_id and autoeval_label")
        if isinstance(label, str):
            normalized = label.strip().lower() in {"1", "true", "yes", "pass", "correct"}
        else:
            normalized = bool(label)
        labels.append({
            "case_id": str(case_id), "repeat": args.repeat,
            "judge_label": normalized, "judge_id": args.judge_id,
            "source_sha256": sha256_file(args.input.resolve()), "imported_at": utc_now(),
        })
    output = workspace / "judgments" / args.condition / args.split / f"repeat-{args.repeat}.jsonl"
    write_jsonl(output, labels)
    print(json.dumps({"output": str(output), "n": len(labels), "judge_id": args.judge_id}, indent=2))
    return 0


def command_evaluate(args: argparse.Namespace) -> int:
    workspace = args.workspace.resolve()
    gold = {str(row["case_id"]): row for row in read_jsonl(workspace / "sealed" / "gold.jsonl")}
    conditions = args.conditions.split(",") if args.conditions else [p.name for p in (workspace / "runs").iterdir() if p.is_dir()]
    evaluated: dict[str, list[dict[str, Any]]] = {}
    summary: dict[str, Any] = {}
    for condition in conditions:
        rows = _load_condition(workspace, condition, args.split)
        scored = []
        for row in rows:
            gold_row = gold[str(row["case_id"])]
            expected = gold_row["evidence_session_ids"]
            forbidden = set(gold_row.get("forbidden_session_ids", []))
            scored_row = {
                **row,
                **retrieval_metrics(row["retrieved_session_ids"], expected, args.top_k),
                "contaminated": bool(row.get("contaminated")) or bool(forbidden & set(row["retrieved_session_ids"])),
                "abstention_correct": (
                    not row["retrieved_session_ids"] if gold_row.get("expects_abstention") else None
                ),
                "extraction_correct": (
                    set(gold_row.get("expected_object_types", [])).issubset(set(row.get("extracted_object_types", [])))
                    if gold_row.get("expected_object_types") else None
                ),
            }
            scored.append(scored_row)
        evaluated[condition] = scored
        contamination_n = len(scored)
        contamination_events = sum(bool(r["contaminated"]) for r in scored)
        latencies = [float(r["latency_ms"]) for r in scored if r.get("latency_ms") is not None]
        summary[condition] = {
            "n": len(scored), "qa_accuracy": mean(r.get("qa_accuracy") for r in scored),
            "recall_at_5": mean(r.get("recall_at_k") for r in scored),
            "precision_at_5": mean(r.get("precision_at_k") for r in scored),
            "mrr": mean(r.get("mrr") for r in scored),
            "contamination_rate": contamination_events / contamination_n if contamination_n else None,
            "zero_contamination_upper_95": zero_event_upper_95(contamination_n) if contamination_events == 0 else None,
            "citation_fidelity": mean(r.get("citation_fidelity") for r in scored),
            "correction_rate": mean(r.get("correction_rate") for r in scored),
            "abstention_accuracy": mean(float(r["abstention_correct"]) for r in scored if r.get("abstention_correct") is not None),
            "extraction_accuracy": mean(float(r["extraction_correct"]) for r in scored if r.get("extraction_correct") is not None),
            "latency_ms_mean": mean(r.get("latency_ms") for r in scored),
            "latency_ms_p95": percentile(latencies, 0.95) if latencies else None,
            "input_tokens_mean": mean(r.get("input_tokens") for r in scored),
            "error_rate": mean(float(bool(r.get("error"))) for r in scored),
            "by_ability": {
                ability: {
                    "n": len(group), "qa_accuracy": mean(r.get("qa_accuracy") for r in group),
                    "recall_at_5": mean(r.get("recall_at_k") for r in group),
                    "contamination_rate": mean(float(bool(r.get("contaminated"))) for r in group),
                    "abstention_accuracy": mean(float(r["abstention_correct"]) for r in group if r.get("abstention_correct") is not None),
                    "extraction_accuracy": mean(float(r["extraction_correct"]) for r in group if r.get("extraction_correct") is not None),
                }
                for ability, group in _group(scored, "ability").items()
            },
        }
    contrast = None
    if "full" in evaluated and "no-consolidation" in evaluated:
        metric = "qa_accuracy" if any(r.get("qa_accuracy") is not None for r in evaluated["full"]) else "recall_at_k"
        contrast = paired_bootstrap(
            evaluated["full"], evaluated["no-consolidation"], metric,
            iterations=args.bootstrap, seed=args.seed,
            cluster_key="cluster_id" if args.cluster_bootstrap else None,
        )
        contrast.update({
            "metric": metric,
            "randomization_p": paired_randomization_test(
                evaluated["full"], evaluated["no-consolidation"], metric,
                iterations=args.randomizations, seed=args.seed,
            ),
        })
        ci_low = contrast["ci95"][0]
        contrast["primary_pass"] = bool(
            contrast["effect"] is not None and contrast["effect"] >= DecisionThresholds().minimum_effect
            and ci_low is not None and ci_low > 0
            and summary["full"]["contamination_rate"] == 0
        )
    thresholds = DecisionThresholds()
    full = summary.get("full", {})
    full_abilities = full.get("by_ability", {})
    long_context = summary.get("long-context", {})
    token_reduction = None
    if full.get("input_tokens_mean") is not None and long_context.get("input_tokens_mean"):
        token_reduction = 1 - full["input_tokens_mean"] / long_context["input_tokens_mean"]
    operational = {
        "contamination_zero": full.get("contamination_rate") == thresholds.contamination_max if full else None,
        "cross_scope_allowed": _gate(full_abilities, "cross-scope-allowed", "recall_at_5", thresholds.cross_scope_recall_min),
        "temporal_update": _gate(full_abilities, "knowledge-update", "recall_at_5", thresholds.temporal_accuracy_min),
        "citation_fidelity": _at_least(full.get("citation_fidelity"), thresholds.citation_fidelity_min),
        "catalog_p95_ms": _at_most(summary.get("catalog-only", {}).get("latency_ms_p95"), 5000.0),
        "correction_rate": _at_most(full.get("correction_rate"), thresholds.correction_rate_max),
        "token_reduction": _at_least(token_reduction, thresholds.token_reduction_min),
        "token_reduction_value": token_reduction,
    }
    result = {
        "protocol_version": PROTOCOL_VERSION, "evaluated_at": utc_now(),
        "split": args.split, "bootstrap_iterations": args.bootstrap,
        "randomization_iterations": args.randomizations,
        "conditions": summary, "primary_contrast": contrast,
        "operational_gates": operational,
        "interpretation": "pass" if contrast and contrast["primary_pass"] else ("fail" if contrast else "descriptive-only"),
    }
    out = workspace / "evaluation" / f"{args.split}.json"
    write_json(out, result)
    for condition, rows in evaluated.items():
        write_jsonl(workspace / "evaluation" / f"{args.split}-{condition}-scored.jsonl", rows)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def _at_least(value: float | None, threshold: float) -> bool | None:
    return None if value is None else value >= threshold


def _at_most(value: float | None, threshold: float) -> bool | None:
    return None if value is None else value <= threshold


def _gate(by_ability: dict[str, Any], ability: str, metric: str, threshold: float) -> bool | None:
    return _at_least(by_ability.get(ability, {}).get(metric), threshold)


def _group(rows: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row.get(key, "unknown"))].append(row)
    return dict(grouped)


def command_audit_sample(args: argparse.Namespace) -> int:
    workspace = args.workspace.resolve()
    source = read_jsonl(workspace / "evaluation" / f"{args.split}-{args.condition}-scored.jsonl")
    selected = audit_sample(source, args.fraction, args.seed)
    rows = [{
        "case_id": r["case_id"], "ability": r["ability"], "hypothesis": r.get("hypothesis"),
        "automatic_label": r.get("judge_label"), "rater_1": None, "rater_2": None,
        "adjudicated_label": None, "notes": None,
    } for r in selected]
    out = workspace / "audit" / f"{args.split}-{args.condition}.jsonl"
    write_jsonl(out, rows)
    print(json.dumps({"output": str(out), "n": len(rows), "fraction": args.fraction}, indent=2))
    return 0


def command_audit_score(args: argparse.Namespace) -> int:
    rows = read_jsonl(args.input.resolve())
    complete = [r for r in rows if r.get("rater_1") is not None and r.get("rater_2") is not None]
    kappa = cohens_kappa([r["rater_1"] for r in complete], [r["rater_2"] for r in complete])
    consensus = [r for r in complete if r.get("adjudicated_label") is not None]
    auto_accuracy = mean(float(r.get("automatic_label") == r.get("adjudicated_label")) for r in consensus)
    result = {"n": len(rows), "double_rated": len(complete), "adjudicated": len(consensus), "cohens_kappa": kappa, "automatic_agreement": auto_accuracy}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def command_report(args: argparse.Namespace) -> int:
    workspace = args.workspace.resolve()
    evaluation = json.loads((workspace / "evaluation" / f"{args.split}.json").read_text(encoding="utf-8"))
    lines = [
        f"# Acervo public memory benchmark — {args.split}", "",
        f"Generated: {evaluation['evaluated_at']} · protocol {evaluation['protocol_version']}", "",
        "## Conditions", "",
        "| Condition | n | QA accuracy | Recall@5 | Precision@5 | Contamination | Mean latency |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    pct = lambda x: "—" if x is None else f"{100*x:.1f}%"
    for name, data in evaluation["conditions"].items():
        latency = "—" if data["latency_ms_mean"] is None else f"{data['latency_ms_mean']:.0f} ms"
        lines.append(
            f"| {name} | {data['n']} | {pct(data['qa_accuracy'])} | {pct(data['recall_at_5'])} | "
            f"{pct(data['precision_at_5'])} | {pct(data['contamination_rate'])} | "
            f"{latency} |"
        )
    contrast = evaluation.get("primary_contrast")
    lines += ["", "## Primary confirmatory contrast", ""]
    if contrast:
        if contrast.get("effect") is None:
            lines.append("Unavailable: the paired conditions have no common scored observations.")
        else:
            lines += [
                f"Full − no-consolidation on `{contrast['metric']}`: **{contrast['effect']*100:+.1f} points** "
                f"(95% CI {contrast['ci95'][0]*100:+.1f} to {contrast['ci95'][1]*100:+.1f}; "
                f"paired randomization p={contrast['randomization_p']:.4g}).",
                "", f"Decision: **{'PASS' if contrast['primary_pass'] else 'FAIL / INCONCLUSIVE'}**.",
            ]
    else:
        lines.append("Not available: both `full` and `no-consolidation` runs are required.")
    lines += [
        "", "## Interpretation rules", "",
        "A benefit claim requires ≥5 percentage points, a strictly positive lower 95% confidence bound, "
        "and zero observed contamination. Missing judge labels produce retrieval-only descriptive results.", "",
        "## Operational gates", "",
    ]
    for name, value in evaluation.get("operational_gates", {}).items():
        if name.endswith("_value"):
            continue
        label = "not measured" if value is None else ("pass" if value else "fail")
        lines.append(f"- `{name}`: **{label}**")
    lines.append("")
    out = workspace / "evaluation" / f"{args.split}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(str(out))
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--workspace", type=Path, default=DEFAULT_WORKSPACE)

    prep = sub.add_parser("prepare", parents=[common])
    prep.add_argument("--dataset", choices=("longmemeval-s", "locomo", "acervo-native"), required=True)
    prep.add_argument("--source", type=Path)
    prep.add_argument("--download", action="store_true")
    prep.add_argument("--pilot-size", type=int, default=50)
    prep.add_argument("--seed", type=int, default=20260713)
    prep.set_defaults(func=command_prepare)

    run = sub.add_parser("run", parents=[common])
    run.add_argument("--condition", choices=CONDITIONS, required=True)
    run.add_argument("--split", default="pilot", choices=("pilot", "confirmatory", "replication", "all"))
    run.add_argument("--repeat", type=int, default=1)
    run.add_argument("--seed", type=int, default=20260713)
    run.add_argument("--top-k", type=int, default=5)
    run.add_argument("--adapter-command")
    run.add_argument("--reader-command")
    run.add_argument("--adapter-id", default="unspecified")
    run.add_argument("--consolidator-id")
    run.add_argument("--model-id", default="not-run")
    run.add_argument("--judge-id", default="not-run")
    run.add_argument("--code-version", default="unknown")
    run.add_argument("--timeout", type=int, default=600)
    run.add_argument("--fail-on-error", action="store_true")
    run.set_defaults(func=command_run)

    ev = sub.add_parser("evaluate", parents=[common])
    ev.add_argument("--split", default="confirmatory")
    ev.add_argument("--conditions", help="comma separated; default: discovered")
    ev.add_argument("--top-k", type=int, default=5)
    ev.add_argument("--bootstrap", type=int, default=10_000)
    ev.add_argument("--randomizations", type=int, default=100_000)
    ev.add_argument("--seed", type=int, default=20260713)
    ev.add_argument("--cluster-bootstrap", action="store_true")
    ev.set_defaults(func=command_evaluate)

    audit = sub.add_parser("audit-sample", parents=[common])
    audit.add_argument("--split", default="confirmatory")
    audit.add_argument("--condition", default="full")
    audit.add_argument("--fraction", type=float, default=0.10)
    audit.add_argument("--seed", type=int, default=20260713)
    audit.set_defaults(func=command_audit_sample)
    score = sub.add_parser("audit-score")
    score.add_argument("--input", type=Path, required=True)
    score.set_defaults(func=command_audit_score)
    export = sub.add_parser("export-qa", parents=[common])
    export.add_argument("--condition", required=True, choices=CONDITIONS)
    export.add_argument("--split", default="confirmatory")
    export.add_argument("--repeat", type=int, default=1)
    export.add_argument("--output", type=Path)
    export.set_defaults(func=command_export_qa)
    imported = sub.add_parser("import-judge", parents=[common])
    imported.add_argument("--input", type=Path, required=True)
    imported.add_argument("--condition", required=True, choices=CONDITIONS)
    imported.add_argument("--split", default="confirmatory")
    imported.add_argument("--repeat", type=int, default=1)
    imported.add_argument("--judge-id", required=True)
    imported.set_defaults(func=command_import_judge)
    report = sub.add_parser("report", parents=[common])
    report.add_argument("--split", default="confirmatory")
    report.set_defaults(func=command_report)
    return p


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
