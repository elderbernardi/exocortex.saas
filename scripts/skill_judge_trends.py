#!/usr/bin/env python3
"""
Skill Judge Trend Dashboard — Track verdict evolution across baselines.

Reads timestamped JSON baselines from .dogfood/baselines/ and produces
a markdown trend report showing PASS/IMPROVE/REWRITE counts over time.

Usage:
    python scripts/skill_judge_trends.py                        # print to stdout
    python scripts/skill_judge_trends.py --output trends.md     # save to file
    python scripts/skill_judge_trends.py --json                 # output raw JSON
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BASELINES_DIR = REPO_ROOT / ".dogfood" / "baselines"


def discover_baselines(baselines_dir: Path) -> list[dict]:
    """Find all baseline JSON files and extract metadata."""
    baselines = []
    for f in sorted(baselines_dir.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, Exception):
            continue

        if not isinstance(data, list) or not data:
            continue

        # Check if it has overall_verdict field (skill judge output)
        if not any("overall_verdict" in r for r in data):
            continue

        # Extract timestamp from filename or file mtime
        ts = _extract_timestamp(f)

        # Compute verdict counts
        verdicts = {"PASS": 0, "IMPROVE": 0, "REWRITE": 0}
        dim_coverage = {"D1": 0, "D2": 0, "D3": 0, "D4": 0, "D5": 0}
        for result in data:
            v = result.get("overall_verdict", "REWRITE")
            verdicts[v] = verdicts.get(v, 0) + 1
            dims = result.get("dimensions", {})
            if "D1_structural" in dims:
                dim_coverage["D1"] += 1
            for dk in ["D2_clarity", "D3_alignment", "D4_fitness", "D5_economy"]:
                if dk in dims:
                    dim_coverage[dk.split("_")[0]] += 1

        has_llm = dim_coverage["D2"] > 0

        baselines.append({
            "file": f.name,
            "path": str(f),
            "timestamp": ts,
            "skill_count": len(data),
            "verdicts": verdicts,
            "dim_coverage": dim_coverage,
            "has_llm": has_llm,
            "type": "live" if has_llm else "d1-only",
        })

    return sorted(baselines, key=lambda x: x["timestamp"])


def _extract_timestamp(path: Path) -> str:
    """Extract a sortable timestamp from filename or fall back to mtime."""
    name = path.stem
    # Match patterns like: d1d5-sweep-20260610-234500
    ts_match = re.search(r"(\d{8})-?(\d{6})", name)
    if ts_match:
        date_str = ts_match.group(1)
        time_str = ts_match.group(2)
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}T{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}"

    # Match date-only patterns
    date_match = re.search(r"(\d{4})-?(\d{2})-?(\d{2})", name)
    if date_match:
        return f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}T00:00:00"

    # Fallback to file mtime
    mtime = datetime.fromtimestamp(path.stat().st_mtime)
    return mtime.strftime("%Y-%m-%dT%H:%M:%S")


def _sparkline(values: list[int], max_val: int) -> str:
    """Generate a simple ASCII sparkline."""
    blocks = " ▁▂▃▄▅▆▇█"
    if max_val == 0:
        return "".join("▁" for _ in values)
    return "".join(blocks[min(int(v / max_val * 8), 8)] for v in values)


def generate_trend_report(baselines: list[dict]) -> str:
    """Generate a markdown trend report."""
    lines = ["# Skill Judge — Trend Dashboard\n"]
    lines.append(f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"> Baselines found: {len(baselines)}\n")

    if not baselines:
        lines.append("No baseline files found in `.dogfood/baselines/`.\n")
        return "\n".join(lines)

    # Summary of latest
    latest = baselines[-1]
    v = latest["verdicts"]
    total = latest["skill_count"]
    pass_pct = (v["PASS"] / total * 100) if total > 0 else 0
    lines.append(f"## Latest Baseline: `{latest['file']}`\n")
    lines.append(f"- **Skills:** {total}")
    lines.append(f"- **PASS:** {v['PASS']} ({pass_pct:.0f}%)")
    lines.append(f"- **IMPROVE:** {v['IMPROVE']}")
    lines.append(f"- **REWRITE:** {v['REWRITE']}")
    lines.append(f"- **Type:** {latest['type']} ({'includes LLM D2-D5' if latest['has_llm'] else 'D1 only'})\n")

    # Trend table
    lines.append("## Trend Table\n")
    lines.append("| Timestamp | File | Skills | ✅ PASS | ⚠️ IMPROVE | 🔴 REWRITE | Type |")
    lines.append("|---|---|---|---|---|---|---|")

    for b in baselines:
        v = b["verdicts"]
        lines.append(
            f"| {b['timestamp'][:16]} | `{b['file'][:35]}` | {b['skill_count']} | "
            f"{v['PASS']} | {v['IMPROVE']} | {v['REWRITE']} | {b['type']} |"
        )

    # Sparklines (only if >1 baseline)
    if len(baselines) > 1:
        lines.append("\n## Sparklines\n")
        pass_vals = [b["verdicts"]["PASS"] for b in baselines]
        improve_vals = [b["verdicts"]["IMPROVE"] for b in baselines]
        rewrite_vals = [b["verdicts"]["REWRITE"] for b in baselines]
        max_val = max(max(pass_vals), max(improve_vals), max(rewrite_vals), 1)

        lines.append(f"- **PASS:**    `{_sparkline(pass_vals, max_val)}` ({pass_vals[0]} → {pass_vals[-1]})")
        lines.append(f"- **IMPROVE:** `{_sparkline(improve_vals, max_val)}` ({improve_vals[0]} → {improve_vals[-1]})")
        lines.append(f"- **REWRITE:** `{_sparkline(rewrite_vals, max_val)}` ({rewrite_vals[0]} → {rewrite_vals[-1]})")

    # Per-skill delta (compare first vs latest if both have verdicts)
    if len(baselines) >= 2:
        first = baselines[0]
        latest = baselines[-1]

        first_data = json.loads(Path(first["path"]).read_text(encoding="utf-8"))
        latest_data = json.loads(Path(latest["path"]).read_text(encoding="utf-8"))

        first_map = {r["skill_name"]: r["overall_verdict"] for r in first_data if "overall_verdict" in r}
        latest_map = {r["skill_name"]: r["overall_verdict"] for r in latest_data if "overall_verdict" in r}

        improved = []
        regressed = []
        verdict_rank = {"PASS": 0, "IMPROVE": 1, "REWRITE": 2}

        for name in sorted(set(first_map.keys()) & set(latest_map.keys())):
            old_rank = verdict_rank.get(first_map[name], 2)
            new_rank = verdict_rank.get(latest_map[name], 2)
            if new_rank < old_rank:
                improved.append(f"- `{name}`: {first_map[name]} → {latest_map[name]}")
            elif new_rank > old_rank:
                regressed.append(f"- `{name}`: {first_map[name]} → {latest_map[name]}")

        if improved or regressed:
            lines.append(f"\n## Delta: `{first['file']}` → `{latest['file']}`\n")
            if improved:
                lines.append(f"### ✅ Improved ({len(improved)})\n")
                lines.extend(improved)
            if regressed:
                lines.append(f"\n### 🔴 Regressed ({len(regressed)})\n")
                lines.extend(regressed)

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Skill Judge Trend Dashboard")
    parser.add_argument("--baselines-dir", type=Path, default=BASELINES_DIR, help="Baselines directory")
    parser.add_argument("--output", type=str, help="Save report to file")
    parser.add_argument("--json", action="store_true", help="Output raw JSON data")
    args = parser.parse_args()

    baselines = discover_baselines(args.baselines_dir)

    if args.json:
        print(json.dumps(baselines, indent=2, ensure_ascii=False))
        return

    report = generate_trend_report(baselines)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Trend report saved to {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
