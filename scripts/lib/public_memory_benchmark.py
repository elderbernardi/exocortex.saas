#!/usr/bin/env python3
"""Reproducible public-memory benchmark primitives.

The module deliberately keeps preparation, system execution, and scoring in
separate stages.  Gold answers are never included in runner requests.  The
implementation uses only the Python standard library so the statistical report
can be reproduced in CI without installing a scientific stack.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence


LME_URL = (
    "https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/"
    "resolve/main/longmemeval_s_cleaned.json"
)
LOCOMO_URL = "https://raw.githubusercontent.com/snap-research/locomo/main/data/locomo10.json"
CONDITIONS = (
    "full",
    "no-consolidation",
    "catalog-only",
    "flat-no-microverse",
    "long-context",
    "oracle",
)
ABILITY_ORDER = (
    "information-extraction",
    "multi-session-reasoning",
    "knowledge-update",
    "temporal-reasoning",
    "abstention",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(canonical_json(row) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL at {path}:{line_no}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"expected object at {path}:{line_no}")
            rows.append(value)
    return rows


def lme_ability(question_type: str, question_id: str) -> str:
    if question_id.endswith("_abs"):
        return "abstention"
    mapping = {
        "single-session-user": "information-extraction",
        "single-session-assistant": "information-extraction",
        "single-session-preference": "information-extraction",
        "multi-session": "multi-session-reasoning",
        "knowledge-update": "knowledge-update",
        "temporal-reasoning": "temporal-reasoning",
    }
    return mapping.get(question_type, question_type or "unknown")


def _turn_text(turn: dict[str, Any]) -> str:
    content = turn.get("content", "")
    if isinstance(content, list):
        content = " ".join(str(x.get("text", x)) if isinstance(x, dict) else str(x) for x in content)
    return str(content)


def load_longmemeval(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("LongMemEval source must be a JSON array")
    cases: list[dict[str, Any]] = []
    gold: list[dict[str, Any]] = []
    for item in raw:
        required = {"question_id", "question_type", "question", "answer", "haystack_session_ids", "haystack_sessions"}
        missing = sorted(required - set(item))
        if missing:
            raise ValueError(f"LongMemEval item missing fields {missing}")
        ids = [str(x) for x in item["haystack_session_ids"]]
        dates = item.get("haystack_dates") or [None] * len(ids)
        sessions = item["haystack_sessions"]
        if not (len(ids) == len(dates) == len(sessions)):
            raise ValueError(f"misaligned sessions in {item['question_id']}")
        normalized_sessions = []
        for session_id, session_date, turns in zip(ids, dates, sessions):
            normalized_sessions.append({
                "session_id": session_id,
                "date": session_date,
                "turns": [
                    {"role": str(t.get("role", "unknown")), "content": _turn_text(t)}
                    for t in turns
                ],
            })
        qid = str(item["question_id"])
        ability = lme_ability(str(item["question_type"]), qid)
        cases.append({
            "case_id": qid,
            "cluster_id": qid,
            "ability": ability,
            "question_type": str(item["question_type"]),
            "question": str(item["question"]),
            "question_date": item.get("question_date"),
            "sessions": normalized_sessions,
        })
        gold.append({
            "case_id": qid,
            "answer": item["answer"],
            "evidence_session_ids": [str(x) for x in (item.get("answer_session_ids") or [])],
            "expects_abstention": qid.endswith("_abs"),
        })
    return cases, gold


def load_locomo(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("LoCoMo source must be a JSON array")
    cases: list[dict[str, Any]] = []
    gold: list[dict[str, Any]] = []
    for sample in raw:
        sample_id = str(sample.get("sample_id"))
        conversation = sample.get("conversation") or {}
        session_keys = sorted(
            (k for k in conversation if re.fullmatch(r"session_\d+", k)),
            key=lambda k: int(k.split("_")[-1]),
        )
        sessions = []
        dialog_to_session: dict[str, str] = {}
        for key in session_keys:
            turns = conversation[key]
            sid = f"{sample_id}:{key}"
            normalized_turns = []
            for turn in turns:
                dia_id = str(turn.get("dia_id", ""))
                if dia_id:
                    dialog_to_session[dia_id] = sid
                text = str(turn.get("text") or turn.get("blip_caption") or "")
                normalized_turns.append({"role": str(turn.get("speaker", "unknown")), "content": text})
            sessions.append({
                "session_id": sid,
                "date": conversation.get(f"{key}_date_time"),
                "turns": normalized_turns,
            })
        for index, qa in enumerate(sample.get("qa") or []):
            case_id = f"locomo-{sample_id}-{index:04d}"
            evidence = []
            for dialog_id in qa.get("evidence") or []:
                sid = dialog_to_session.get(str(dialog_id))
                if sid and sid not in evidence:
                    evidence.append(sid)
            cases.append({
                "case_id": case_id,
                "cluster_id": sample_id,
                "ability": str(qa.get("category", "unknown")),
                "question_type": str(qa.get("category", "unknown")),
                "question": str(qa.get("question", "")),
                "question_date": None,
                "sessions": sessions,
            })
            gold.append({
                "case_id": case_id,
                "answer": qa.get("answer"),
                "evidence_session_ids": evidence,
                "expects_abstention": False,
            })
    return cases, gold


def load_acervo_native(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Load the generated scope/temporal/adversarial Acervo-native suite."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    items = raw.get("cases") if isinstance(raw, dict) else None
    if not isinstance(items, list):
        raise ValueError("Acervo-native source requires a JSON object with cases[]")
    cases, gold = [], []
    for item in items:
        required = {"case_id", "ability", "question", "sessions", "expected_session_ids"}
        missing = sorted(required - set(item))
        if missing:
            raise ValueError(f"Acervo-native case missing fields {missing}")
        cases.append({
            "case_id": str(item["case_id"]), "cluster_id": str(item.get("cluster_id", item["case_id"])),
            "ability": str(item["ability"]), "question_type": str(item.get("question_type", item["ability"])),
            "question": str(item["question"]), "question_date": item.get("question_date"),
            "scope": str(item.get("scope", "global")), "allow_scopes": list(item.get("allow_scopes", [])),
            "sessions": item["sessions"],
        })
        gold.append({
            "case_id": str(item["case_id"]), "answer": item.get("answer"),
            "evidence_session_ids": [str(x) for x in item["expected_session_ids"]],
            "forbidden_session_ids": [str(x) for x in item.get("forbidden_session_ids", [])],
            "expects_abstention": bool(item.get("expects_abstention", False)),
            "expected_object_types": [str(x) for x in item.get("expected_object_types", [])],
        })
    return cases, gold


def stratified_split(cases: Sequence[dict[str, Any]], pilot_size: int, seed: int) -> dict[str, str]:
    """Return case_id -> split, using equal allocation across LME abilities.

    Remainders and undersized strata are handled deterministically.  This makes
    the intended 10-per-ability pilot exact for the 500-question LME-S dataset.
    """
    if pilot_size < 0 or pilot_size > len(cases):
        raise ValueError("pilot size must be between zero and dataset size")
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        groups[str(case["ability"])].append(case)
    rng = random.Random(seed)
    for group in groups.values():
        group.sort(key=lambda x: x["case_id"])
        rng.shuffle(group)
    chosen: set[str] = set()
    ordered_groups = [g for g in ABILITY_ORDER if g in groups] + sorted(set(groups) - set(ABILITY_ORDER))
    while len(chosen) < pilot_size:
        progressed = False
        for name in ordered_groups:
            available = [x for x in groups[name] if x["case_id"] not in chosen]
            if available and len(chosen) < pilot_size:
                chosen.add(str(available[0]["case_id"]))
                progressed = True
        if not progressed:
            break
    return {str(c["case_id"]): ("pilot" if c["case_id"] in chosen else "confirmatory") for c in cases}


def retrieval_metrics(retrieved: Sequence[str], expected: Sequence[str], k: int = 5) -> dict[str, float | None]:
    top = list(retrieved[:k])
    expected_set = set(expected)
    if not expected_set:
        return {"recall_at_k": None, "precision_at_k": None, "mrr": None}
    hits = [x for x in top if x in expected_set]
    reciprocal = next((1.0 / (i + 1) for i, value in enumerate(top) if value in expected_set), 0.0)
    return {
        "recall_at_k": len(set(hits)) / len(expected_set),
        "precision_at_k": len(hits) / len(top) if top else 0.0,
        "mrr": reciprocal,
    }


def mean(values: Iterable[float | None]) -> float | None:
    clean = [float(v) for v in values if v is not None]
    return sum(clean) / len(clean) if clean else None


def percentile(values: Sequence[float], q: float) -> float:
    if not values:
        raise ValueError("percentile of empty sample")
    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] * (hi - pos) + ordered[hi] * (pos - lo)


def paired_bootstrap(
    rows_a: Sequence[dict[str, Any]],
    rows_b: Sequence[dict[str, Any]],
    metric: str,
    *,
    iterations: int = 10_000,
    seed: int = 20260713,
    cluster_key: str | None = None,
) -> dict[str, Any]:
    """Percentile CI for A-B, paired by case and optionally cluster-resampled."""
    a = {str(r["case_id"]): r for r in rows_a}
    b = {str(r["case_id"]): r for r in rows_b}
    ids = sorted(set(a) & set(b))
    pairs = [(a[i], b[i]) for i in ids if a[i].get(metric) is not None and b[i].get(metric) is not None]
    if not pairs:
        return {"n": 0, "effect": None, "ci95": [None, None], "iterations": iterations}
    units: list[list[tuple[dict[str, Any], dict[str, Any]]]]
    if cluster_key:
        grouped: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
        for pair in pairs:
            grouped[str(pair[0].get(cluster_key, pair[0]["case_id"]))].append(pair)
        units = list(grouped.values())
    else:
        units = [[pair] for pair in pairs]
    observed = statistics.fmean(float(x.get(metric)) - float(y.get(metric)) for x, y in pairs)
    rng = random.Random(seed)
    draws = []
    for _ in range(iterations):
        sampled_units = [units[rng.randrange(len(units))] for _ in units]
        sampled_pairs = [pair for unit in sampled_units for pair in unit]
        draws.append(statistics.fmean(float(x[metric]) - float(y[metric]) for x, y in sampled_pairs))
    return {
        "n": len(pairs),
        "units": len(units),
        "effect": observed,
        "ci95": [percentile(draws, 0.025), percentile(draws, 0.975)],
        "iterations": iterations,
        "seed": seed,
    }


def paired_randomization_test(
    rows_a: Sequence[dict[str, Any]], rows_b: Sequence[dict[str, Any]], metric: str,
    *, iterations: int = 100_000, seed: int = 20260713,
) -> float | None:
    a = {str(r["case_id"]): r for r in rows_a}
    b = {str(r["case_id"]): r for r in rows_b}
    diffs = [
        float(a[i][metric]) - float(b[i][metric])
        for i in sorted(set(a) & set(b))
        if a[i].get(metric) is not None and b[i].get(metric) is not None
    ]
    if not diffs:
        return None
    observed = abs(statistics.fmean(diffs))
    rng = random.Random(seed)
    extreme = 0
    for _ in range(iterations):
        permuted = statistics.fmean(d if rng.random() < 0.5 else -d for d in diffs)
        extreme += abs(permuted) >= observed - 1e-15
    return (extreme + 1) / (iterations + 1)


def holm_bonferroni(p_values: dict[str, float], alpha: float = 0.05) -> dict[str, dict[str, Any]]:
    ordered = sorted(p_values.items(), key=lambda item: item[1])
    out: dict[str, dict[str, Any]] = {}
    still_rejecting = True
    m = len(ordered)
    for index, (name, p_value) in enumerate(ordered):
        threshold = alpha / (m - index)
        reject = still_rejecting and p_value <= threshold
        if not reject:
            still_rejecting = False
        out[name] = {"p": p_value, "threshold": threshold, "reject": reject}
    return out


def zero_event_upper_95(n: int) -> float | None:
    """One-sided exact binomial 95% upper bound when zero events are observed."""
    return None if n <= 0 else 1.0 - 0.05 ** (1.0 / n)


def cohens_kappa(labels_a: Sequence[Any], labels_b: Sequence[Any]) -> float | None:
    if len(labels_a) != len(labels_b) or not labels_a:
        return None
    observed = sum(a == b for a, b in zip(labels_a, labels_b)) / len(labels_a)
    ca, cb = Counter(labels_a), Counter(labels_b)
    expected = sum((ca[k] / len(labels_a)) * (cb[k] / len(labels_b)) for k in set(ca) | set(cb))
    return 1.0 if expected == 1.0 and observed == 1.0 else (observed - expected) / (1.0 - expected)


def audit_sample(rows: Sequence[dict[str, Any]], fraction: float, seed: int) -> list[dict[str, Any]]:
    if not 0 < fraction <= 1:
        raise ValueError("audit fraction must be in (0, 1]")
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get("ability", "unknown"))].append(row)
    rng = random.Random(seed)
    selected: list[dict[str, Any]] = []
    target = max(1, math.ceil(len(rows) * fraction))
    for name in sorted(groups):
        group = sorted(groups[name], key=lambda x: str(x["case_id"]))
        rng.shuffle(group)
        count = max(1, round(target * len(group) / len(rows)))
        selected.extend(group[:count])
    if len(selected) > target:
        rng.shuffle(selected)
        selected = selected[:target]
    elif len(selected) < target:
        present = {str(x["case_id"]) for x in selected}
        remaining = [x for x in rows if str(x["case_id"]) not in present]
        rng.shuffle(remaining)
        selected.extend(remaining[: target - len(selected)])
    return sorted(selected, key=lambda x: str(x["case_id"]))


def immutable_receipt(row: dict[str, Any]) -> dict[str, Any]:
    receipt = dict(row)
    receipt["receipt_sha256"] = sha256_bytes(canonical_json(row).encode("utf-8"))
    return receipt


@dataclass(frozen=True)
class DecisionThresholds:
    minimum_effect: float = 0.05
    contamination_max: float = 0.0
    cross_scope_recall_min: float = 0.80
    temporal_accuracy_min: float = 0.90
    citation_fidelity_min: float = 0.95
    token_reduction_min: float = 0.25
    accuracy_loss_max: float = 0.02
    correction_rate_max: float = 0.10


def manifest_hashes(paths: Iterable[Path], root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): sha256_file(p) for p in sorted(paths)}
