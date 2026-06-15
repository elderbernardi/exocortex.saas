#!/usr/bin/env python3
"""
GEPA Loop Orchestrator — Closed-loop skill improvement via judge → rewrite → re-judge.

Usage:
    python scripts/gepa_loop.py --all                    # all non-PASS skills
    python scripts/gepa_loop.py --skill excrtx-foo       # specific skill
    python scripts/gepa_loop.py --rewrite-only            # REWRITE verdict only
    python scripts/gepa_loop.py --improve-only            # IMPROVE verdict only
    python scripts/gepa_loop.py --dry-run                 # simulate without writing
    python scripts/gepa_loop.py --max-attempts 3          # attempts per skill
    python scripts/gepa_loop.py --baseline FILE           # reference baseline
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.skill_judge import (
    discover_skills,
    parse_skill,
    check_d1_structural,
    compute_overall_verdict,
    collect_priority_fixes,
    call_llm_judge,
    build_judge_prompt,
    SKILLS_DIR,
    REPO_ROOT,
    RUBRIC_PATH,
    SOUL_SEED_PATH,
)
from scripts.gepa_rewriter import (
    rewrite_skill,
    RewriteResult,
    STRATEGIES,
)

RUNS_DIR = REPO_ROOT / ".dogfood" / "runs" / "gepa"

# Verdict ranking: lower = better
VERDICT_RANK = {"PASS": 0, "IMPROVE": 1, "REWRITE": 2}


def _load_baseline(baseline_path: Path) -> dict:
    """Load baseline JSON and return a dict keyed by skill_name."""
    data = json.loads(baseline_path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {r["skill_name"]: r for r in data}
    return data


def _get_soul_context() -> str:
    """Read and truncate SOUL_SEED.md for prompt context."""
    if SOUL_SEED_PATH.exists():
        text = SOUL_SEED_PATH.read_text(encoding="utf-8")
        return text[:3000]
    return "No SOUL_SEED.md available."


def _get_rubric_text() -> str:
    """Read rubric for prompt context."""
    if RUBRIC_PATH.exists():
        return RUBRIC_PATH.read_text(encoding="utf-8")
    return "No rubric available."


def _git_backup_skill(skill_path: Path) -> str | None:
    """Read original content as backup."""
    if skill_path.exists():
        return skill_path.read_text(encoding="utf-8")
    return None


def _git_rollback_skill(skill_path: Path, original_content: str):
    """Restore skill to original content."""
    skill_path.write_text(original_content, encoding="utf-8")


def _git_commit_skill(skill_path: Path, skill_name: str, verdict_before: str, verdict_after: str):
    """Stage and commit a single skill."""
    try:
        subprocess.run(
            ["git", "add", str(skill_path)],
            cwd=REPO_ROOT, check=True, capture_output=True,
        )
        msg = f"fix(skill): GEPA {verdict_before} → {verdict_after} for {skill_name}"
        subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=REPO_ROOT, check=True, capture_output=True,
        )
        print(f"    📦 Committed: {msg}", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"    ⚠️ Git commit failed: {e}", file=sys.stderr)


def _judge_skill_d1(skill_path: Path) -> dict:
    """Quick D1-only check (deterministic, no LLM needed)."""
    parsed = parse_skill(skill_path)
    return check_d1_structural(parsed)


def _judge_skill_full(skill_path: Path, skill_name: str) -> dict:
    """Full D1-D5 judge (requires LLM for D2-D5)."""
    parsed = parse_skill(skill_path)
    d1 = check_d1_structural(parsed)

    rubric = _get_rubric_text()
    soul = _get_soul_context()

    # Build the judge prompt and call LLM
    prompt = build_judge_prompt(parsed, rubric, soul)
    d2d5 = call_llm_judge(prompt)

    if d2d5:
        verdict = compute_overall_verdict(d1, d2d5)
    else:
        verdict = "PASS" if d1["label"] == "COMPLIANT" else (
            "IMPROVE" if d1["label"] == "PARTIAL" else "REWRITE"
        )

    return {
        "skill_name": skill_name,
        "dimensions": {"D1_structural": d1, **(d2d5 or {})},
        "overall_verdict": verdict,
        "priority_fixes": collect_priority_fixes(d1, d2d5 or {}),
    }


def process_skill(
    skill_name: str,
    skill_path: Path,
    judge_result: dict,
    rubric_text: str,
    soul_context: str,
    max_attempts: int = 3,
    dry_run: bool = False,
    auto_commit: bool = True,
) -> dict:
    """Run the GEPA loop for a single skill. Returns a per-skill audit entry."""
    verdict_before = judge_result["overall_verdict"]
    entry = {
        "skill": skill_name,
        "before_verdict": verdict_before,
        "after_verdict": verdict_before,
        "attempts": 0,
        "strategy_used": "",
        "llm_model": "",
        "changes_summary": "",
        "d1_regression": False,
        "error": None,
    }

    print(f"\n  🎯 {skill_name} (current: {verdict_before})", file=sys.stderr)

    # Backup original
    original_content = _git_backup_skill(skill_path)
    if not original_content:
        entry["error"] = "Could not read skill file"
        return entry

    # Original D1 for regression check
    orig_d1 = _judge_skill_d1(skill_path)
    orig_d1_label = orig_d1["label"]

    for attempt in range(1, max_attempts + 1):
        strategy = STRATEGIES[min(attempt - 1, len(STRATEGIES) - 1)]
        entry["attempts"] = attempt
        entry["strategy_used"] = strategy

        print(f"    Attempt {attempt}/{max_attempts} (strategy: {strategy})...", file=sys.stderr)

        if dry_run:
            print(f"    🏜️ DRY RUN — skipping actual rewrite", file=sys.stderr)
            entry["changes_summary"] = "dry-run: no changes"
            return entry

        # Rewrite
        result = rewrite_skill(
            skill_name, skill_path, judge_result, rubric_text, soul_context, strategy
        )
        entry["llm_model"] = result.llm_model

        if not result.success:
            print(f"    ❌ Rewrite failed: {result.validation_errors}", file=sys.stderr)
            entry["error"] = f"Validation: {result.validation_errors}"
            if attempt < max_attempts:
                continue
            return entry

        # Write new content
        skill_path.write_text(result.new_content, encoding="utf-8")

        # D1 gate (quick, deterministic)
        new_d1 = _judge_skill_d1(skill_path)
        if new_d1["label"] != "COMPLIANT" and orig_d1_label == "COMPLIANT":
            print(f"    🛑 D1 REGRESSION: {orig_d1_label} → {new_d1['label']} — HARD REJECT", file=sys.stderr)
            _git_rollback_skill(skill_path, original_content)
            entry["d1_regression"] = True
            entry["error"] = f"D1 regressed: {orig_d1_label} → {new_d1['label']}"
            if attempt < max_attempts:
                continue
            return entry

        # Full re-judge
        print(f"    🔍 Re-judging...", file=sys.stderr)
        new_judge = _judge_skill_full(skill_path, skill_name)
        new_verdict = new_judge["overall_verdict"]

        # Compare verdicts
        old_rank = VERDICT_RANK.get(verdict_before, 9)
        new_rank = VERDICT_RANK.get(new_verdict, 9)

        if new_rank < old_rank:
            # Improved!
            print(f"    ✅ PROMOTED: {verdict_before} → {new_verdict}", file=sys.stderr)
            entry["after_verdict"] = new_verdict
            entry["changes_summary"] = result.changes_summary
            if auto_commit and not dry_run:
                _git_commit_skill(skill_path, skill_name, verdict_before, new_verdict)
            return entry
        else:
            # No improvement — rollback
            print(f"    ⬅️ No improvement ({verdict_before} → {new_verdict}) — rollback", file=sys.stderr)
            _git_rollback_skill(skill_path, original_content)
            if attempt < max_attempts:
                continue

    entry["error"] = f"Exhausted {max_attempts} attempts without improvement"
    return entry


def _save_audit_log(entries: list[dict], run_id: str):
    """Save audit log JSON."""
    RUNS_DIR.mkdir(parents=True, exist_ok=True)

    promotions = sum(1 for e in entries if e["before_verdict"] != e["after_verdict"])
    regressions = sum(1 for e in entries if e.get("d1_regression"))

    audit = {
        "run_id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "skills_attempted": len(entries),
        "skills_promoted": promotions,
        "skills_failed": len(entries) - promotions,
        "d1_regressions": regressions,
        "per_skill": entries,
    }

    path = RUNS_DIR / f"{run_id}.json"
    path.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n📋 Audit log saved to {path}", file=sys.stderr)
    return audit


def main():
    parser = argparse.ArgumentParser(description="GEPA Loop — Automated skill improvement")
    parser.add_argument("--all", action="store_true", help="Process all non-PASS skills")
    parser.add_argument("--skill", type=str, help="Process a specific skill by name")
    parser.add_argument("--rewrite-only", action="store_true", help="Only process REWRITE skills")
    parser.add_argument("--improve-only", action="store_true", help="Only process IMPROVE skills")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without writing changes")
    parser.add_argument("--max-attempts", type=int, default=3, help="Max rewrite attempts per skill")
    parser.add_argument("--baseline", type=str, help="Path to baseline JSON for initial verdicts")
    parser.add_argument("--no-commit", action="store_true", help="Don't auto-commit improvements")
    args = parser.parse_args()

    if not args.all and not args.skill:
        parser.error("Specify --all or --skill <name>")

    # Load baseline or run judge
    baseline = {}
    if args.baseline:
        baseline = _load_baseline(Path(args.baseline))
        print(f"📊 Loaded baseline: {len(baseline)} skills", file=sys.stderr)

    rubric_text = _get_rubric_text()
    soul_context = _get_soul_context()

    # Discover skills
    all_skill_paths = {p.parent.name: p for p in discover_skills(SKILLS_DIR)}

    # Filter skills to process
    skills_to_process = []
    for skill_name, skill_path in sorted(all_skill_paths.items()):
        if args.skill and skill_name != args.skill:
            continue

        if skill_name in baseline:
            judge_result = baseline[skill_name]
        else:
            # Run judge to get current verdict
            print(f"  📏 Judging {skill_name}...", file=sys.stderr)
            judge_result = _judge_skill_full(skill_path, skill_name)

        verdict = judge_result.get("overall_verdict", "PASS")

        if verdict == "PASS":
            continue
        if args.rewrite_only and verdict != "REWRITE":
            continue
        if args.improve_only and verdict != "IMPROVE":
            continue

        skills_to_process.append((skill_name, skill_path, judge_result))

    if not skills_to_process:
        print("No skills to process.", file=sys.stderr)
        return

    print(f"\n🚀 GEPA Loop — {len(skills_to_process)} skills to process", file=sys.stderr)
    if args.dry_run:
        print("🏜️  DRY RUN MODE — no files will be modified", file=sys.stderr)

    # Process skills
    run_id = f"gepa-{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H-%M-%S')}"
    entries = []

    for skill_name, skill_path, judge_result in skills_to_process:
        entry = process_skill(
            skill_name, skill_path, judge_result,
            rubric_text, soul_context,
            max_attempts=args.max_attempts,
            dry_run=args.dry_run,
            auto_commit=not args.no_commit,
        )
        entries.append(entry)

    # Save audit log
    audit = _save_audit_log(entries, run_id)

    # Summary
    print(f"\n{'='*50}", file=sys.stderr)
    print(f"📊 GEPA Run Summary: {run_id}", file=sys.stderr)
    print(f"   Skills attempted: {audit['skills_attempted']}", file=sys.stderr)
    print(f"   Skills promoted:  {audit['skills_promoted']}", file=sys.stderr)
    print(f"   Skills failed:    {audit['skills_failed']}", file=sys.stderr)
    print(f"   D1 regressions:   {audit['d1_regressions']}", file=sys.stderr)

    for e in entries:
        if e["before_verdict"] != e["after_verdict"]:
            emoji = "✅"
        else:
            emoji = "❌"
        print(f"   {emoji} {e['skill']}: {e['before_verdict']} → {e['after_verdict']} ({e['attempts']} attempts)", file=sys.stderr)


if __name__ == "__main__":
    main()
