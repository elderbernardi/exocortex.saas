#!/usr/bin/env python3
"""Materializa um report JSON do memory-eval como knowledge canônico no Acervo.

Uso típico:
  python3 scripts/file_memory_eval_knowledge.py \
    --acervo-root "$ACERVO" \
    --report-json tests/memory-eval/report/live-2026-07-12.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts" / "validate_frontmatter.py"


def pct(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value * 100:.1f}%"


def intfmt(value: Any) -> str:
    if value is None:
        return "—"
    return f"{int(value):,}"


def infer_label(report_json: Path) -> str:
    stem = report_json.stem
    parts = stem.split("-")
    if len(parts) >= 4 and all(p.isdigit() for p in parts[-3:]):
        return "-".join(parts[:-3])
    return stem


def yaml_list(items: list[str]) -> str:
    return "[" + ", ".join(f"'{item}'" for item in items) + "]"


def knowledge_path(acervo_root: Path, scope: str, report_json: Path) -> Path:
    return acervo_root / "micro" / scope / "knowledge" / f"memory-eval-{report_json.stem}.md"


def summarize_findings(strategies: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    ranked = []
    for name, payload in strategies.items():
        overall = payload.get("overall", {})
        recall = overall.get("recall")
        if recall is not None:
            ranked.append((recall, name))
    if ranked:
        ranked.sort(reverse=True)
        findings.append(f"Melhor recall: `{ranked[0][1]}` = {pct(ranked[0][0])}.")

    contamination_free = []
    for name, payload in strategies.items():
        contamination = payload.get("overall", {}).get("contamination_rate")
        if contamination == 0:
            contamination_free.append(name)
    if contamination_free:
        findings.append(
            "Contaminação zero em: " + ", ".join(f"`{name}`" for name in contamination_free) + "."
        )

    abstention_ranked = []
    for name, payload in strategies.items():
        abst = payload.get("overall", {}).get("abstention_accuracy")
        if abst is not None:
            abstention_ranked.append((abst, name))
    if abstention_ranked:
        abstention_ranked.sort(reverse=True)
        findings.append(
            f"Melhor abstention: `{abstention_ranked[0][1]}` = {pct(abstention_ranked[0][0])}."
        )
    return findings


def render_markdown(report: dict[str, Any], report_json: Path, scope: str) -> str:
    run_at = report["run_at"]
    run_date = run_at[:10]
    label = infer_label(report_json)
    title = f"Memory eval — {label} ({run_date})"
    tags = ["memory-eval", "phase6", "retrieval-eval"] + [part for part in label.split("-") if part]
    sources = [f"file:{report_json}"]
    report_md = report_json.with_suffix(".md")
    if report_md.exists():
        sources.append(f"file:{report_md}")

    lines = [
        "---",
        "schema: acervo/v0.2",
        "type: knowledge",
        f"title: '{title}'",
        f"description: 'Métricas observadas do memory-eval {label} executado em {run_at}.'",
        f"tags: {yaml_list(tags)}",
        f"timestamp: {run_date}",
        "class: volátil",
        "status: active",
        "epistemic: fact",
        f"created_at: {run_at}",
        f"created: {run_date}",
        f"updated: {run_date}",
        "nature: knowledge",
        "excrtx_type: fact",
        f"scope_slug: {scope}",
        f"sources: {yaml_list(sources)}",
        f"observed_at: {run_date}",
        "confidence: high",
        "---",
        "",
        f"# {title}",
        "",
        f"> Derivado automaticamente de `{report_json}`.",
        "",
        "## Resumo",
        "",
    ]

    for finding in summarize_findings(report.get("strategies", {})):
        lines.append(f"- {finding}")

    if lines[-1] != "":
        lines.append("")

    lines += [
        "## Métricas gerais",
        "",
        "| Strategy | Recall@k | Precision@k | Contamination | Abstention acc. | Avg token cost (chars) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, payload in report.get("strategies", {}).items():
        overall = payload.get("overall", {})
        lines.append(
            f"| {name} | {pct(overall.get('recall'))} | {pct(overall.get('precision'))} | "
            f"{pct(overall.get('contamination_rate'))} | {pct(overall.get('abstention_accuracy'))} | "
            f"{intfmt(overall.get('avg_token_cost'))} |"
        )

    lines += ["", "## Proveniência", ""]
    for source in sources:
        lines.append(f"- `{source}`")

    return "\n".join(lines) + "\n"


def validate_output(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--file", str(path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acervo-root", type=Path, required=True)
    parser.add_argument("--report-json", type=Path, required=True)
    parser.add_argument("--scope", default="exocortex-ops")
    args = parser.parse_args(argv)

    acervo_root = args.acervo_root.resolve()
    report_json = args.report_json.resolve()

    if not report_json.exists():
        print(f"ERROR: report JSON não encontrado: {report_json}", file=sys.stderr)
        return 2
    if not acervo_root.exists():
        print(f"ERROR: acervo root não encontrado: {acervo_root}", file=sys.stderr)
        return 2

    report = json.loads(report_json.read_text(encoding="utf-8"))
    output_path = knowledge_path(acervo_root, args.scope, report_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown(report, report_json, args.scope), encoding="utf-8")

    validation = validate_output(output_path)
    ok = validation.returncode == 0
    payload = {
        "ok": ok,
        "output_path": str(output_path),
        "report_json": str(report_json),
        "validator_exit": validation.returncode,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if not ok:
        if validation.stdout.strip():
            print(validation.stdout.strip(), file=sys.stderr)
        if validation.stderr.strip():
            print(validation.stderr.strip(), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
