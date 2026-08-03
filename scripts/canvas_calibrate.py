#!/usr/bin/env python3
"""
canvas-calibrate.py — F5 Slice A: Canonical Canvas calibration runner (keyless tier).

Usage:
    python3 scripts/canvas-calibrate.py               # default: keyless eval (non-mutating)
    python3 scripts/canvas-calibrate.py --refresh     # mutating: recompile SOUL then eval
    # TODO Task 6: --live  (live LLM tier, not implemented here)

Exit codes:
    0 — all keyless checks PASS (verdict=PASS)
    1 — one or more keyless checks FAIL (verdict=FAIL)

Design note (non-mutating default):
    The default eval does NOT recompile SOUL_SEED.md.  It greps the EXISTING committed
    SOUL_SEED.md for the required conduct blocks — keeping `git status --porcelain` clean
    and making this safe to run in CI without side-effects.
    The `--refresh` flag enables the mutating conscientizar path (recompiles via
    compile_soul.py with no --dry-run), which IS intentionally excluded from the default.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# ── Repo root (resolved once) ──────────────────────────────────────────────────
_SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT    = _SCRIPT_DIR.parent


# ═══════════════════════════════════════════════════════════════════════════════
# 1.  check_soul_conduct_blocks
# ═══════════════════════════════════════════════════════════════════════════════

def check_soul_conduct_blocks(repo: Path) -> tuple[bool, str]:
    """
    Verify that SOUL_SEED.md contains the two conduct-loop/bounds sections and
    the NEVER-narrate tail.

    Non-mutating: reads the existing committed SOUL_SEED.md directly — does NOT
    recompile via compile_soul.py.  Use --refresh (conscientizar) if you want to
    recompile first.
    """
    soul_path = repo / "SOUL_SEED.md"
    if not soul_path.exists():
        return False, f"SOUL_SEED.md not found at {soul_path}"

    text = soul_path.read_text(encoding="utf-8")
    missing = []
    if "## Conduct Loop" not in text:
        missing.append("## Conduct Loop")
    if "## Conduct Bounds" not in text:
        missing.append("## Conduct Bounds")
    if "NEVER narrate" not in text:
        missing.append("NEVER narrate (tail)")

    if missing:
        return False, f"SOUL_SEED.md missing: {', '.join(missing)}"
    return True, "SOUL_SEED.md has ## Conduct Loop, ## Conduct Bounds, NEVER narrate"


# ═══════════════════════════════════════════════════════════════════════════════
# 2.  check_skills_d1
# ═══════════════════════════════════════════════════════════════════════════════

def check_skills_d1(repo: Path) -> tuple[bool, str]:
    """
    Run skill_judge.py --d1-only for excrtx-conduct-loop AND excrtx-conduct-bounds.
    PASS iff both report D1 COMPLIANT.
    """
    judge = repo / "scripts" / "skill_judge.py"
    skills = ("excrtx-conduct-loop", "excrtx-conduct-bounds")
    results = {}
    for skill in skills:
        try:
            out = subprocess.run(
                [sys.executable, str(judge), "--skill", skill, "--d1-only"],
                capture_output=True,
                text=True,
                cwd=str(repo),
            )
            combined = out.stdout + out.stderr
            if "D1=COMPLIANT" in combined or "COMPLIANT → PASS" in combined:
                results[skill] = "COMPLIANT"
            else:
                results[skill] = f"NOT COMPLIANT — {combined.strip()[-200:]}"
        except Exception as exc:
            results[skill] = f"ERROR: {exc}"

    failed = {k: v for k, v in results.items() if v != "COMPLIANT"}
    if failed:
        detail = "; ".join(f"{k}={v}" for k, v in failed.items())
        return False, f"D1 FAIL: {detail}"
    return True, f"D1 COMPLIANT: {', '.join(skills)}"


# ═══════════════════════════════════════════════════════════════════════════════
# 3.  check_dogfood_catalog
# ═══════════════════════════════════════════════════════════════════════════════

def check_dogfood_catalog(repo: Path) -> tuple[bool, str]:
    """
    Run `bash scripts/test-registry.sh dogfood-catalog`.
    PASS iff exit 0 AND EX-60 + EX-61 scenario files exist.
    """
    reg = repo / "scripts" / "test-registry.sh"
    try:
        out = subprocess.run(
            ["bash", str(reg), "dogfood-catalog"],
            capture_output=True,
            text=True,
            cwd=str(repo),
        )
        if out.returncode != 0:
            return False, f"dogfood-catalog exited {out.returncode}: {out.stderr.strip()[-300:]}"
    except Exception as exc:
        return False, f"ERROR running test-registry.sh: {exc}"

    # Extra: EX-60 and EX-61 scenario files must exist
    scenarios_dir = repo / ".dogfood" / "scenarios"
    missing_scenarios = [
        s for s in ("EX-60.yaml", "EX-61.yaml")
        if not (scenarios_dir / s).exists()
    ]
    if missing_scenarios:
        return False, f"dogfood-catalog OK but missing scenario files: {missing_scenarios}"

    return True, "dogfood-catalog exit 0; EX-60.yaml and EX-61.yaml present"


# ═══════════════════════════════════════════════════════════════════════════════
# 4.  check_anti_narration_selftest
# ═══════════════════════════════════════════════════════════════════════════════

def check_anti_narration_selftest(repo: Path) -> tuple[bool, str]:
    """
    Import check_anti_narration from scripts/ and run check_narration on:
      - a narrated fixture (must return hits)
      - a clean fixture (must return [])
    """
    scripts_dir = str(repo / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    try:
        import check_anti_narration as CAN
    except ImportError as exc:
        return False, f"Cannot import check_anti_narration: {exc}"

    # Narrated fixture — contains a fable phase header
    narrated_messages = [
        {"role": "assistant", "content": "Classificação: esta tarefa é de execução."}
    ]
    hits = CAN.check_narration(narrated_messages)
    if not hits:
        return False, "check_narration did NOT detect narration in narrated fixture (false negative)"

    # Clean fixture — plain work output, no phase headers
    clean_messages = [
        {"role": "assistant", "content": "A análise foi concluída. Ver artefato em acervo/_tasks/t1/output.md"}
    ]
    clean_hits = CAN.check_narration(clean_messages)
    if clean_hits:
        return False, f"check_narration raised false-positive on clean fixture: {clean_hits}"

    return True, f"anti-narration selftest: narrated→{hits}, clean→[]"


# ═══════════════════════════════════════════════════════════════════════════════
# 5.  check_primer
# ═══════════════════════════════════════════════════════════════════════════════

PRIMER_REQUIRED_SECTIONS = [
    "# Canvas de Tarefas",
    "## Método",
    "## Loop de condução",
    "## Eventos da Sala",
    "## Contrato de consciência",
    "## Colheita → Receita",
]


def check_primer(repo: Path) -> tuple[bool, str]:
    """
    Verify docs/canvas/AGENT-PRIMER.md exists and has all required section headers.
    """
    primer_path = repo / "docs" / "canvas" / "AGENT-PRIMER.md"
    if not primer_path.exists():
        return False, f"AGENT-PRIMER.md not found at {primer_path}"

    text = primer_path.read_text(encoding="utf-8")
    missing = [h for h in PRIMER_REQUIRED_SECTIONS if h not in text]
    if missing:
        return False, f"AGENT-PRIMER.md missing sections: {missing}"

    return True, f"AGENT-PRIMER.md present with all {len(PRIMER_REQUIRED_SECTIONS)} required sections"


# ═══════════════════════════════════════════════════════════════════════════════
# Conscientizar (mutating — only called with --refresh)
# ═══════════════════════════════════════════════════════════════════════════════

def conscientizar(repo: Path) -> None:
    """
    Mutating: recompile SOUL_SEED.md via compile_soul.py (no --dry-run).
    Only called when the user passes --refresh.  NEVER called during the default eval.
    """
    compile_soul = repo / "scripts" / "compile_soul.py"
    print("  [refresh] Recompiling SOUL_SEED.md via compile_soul.py …")
    out = subprocess.run(
        [sys.executable, str(compile_soul)],
        capture_output=True,
        text=True,
        cwd=str(repo),
    )
    if out.returncode != 0:
        print(f"  [refresh] WARNING: compile_soul.py exited {out.returncode}")
        print(out.stderr.strip())
    else:
        print("  [refresh] SOUL_SEED.md recompiled successfully.")


# ═══════════════════════════════════════════════════════════════════════════════
# run_keyless
# ═══════════════════════════════════════════════════════════════════════════════

def run_keyless(repo: Path) -> dict:
    """
    Run all 5 keyless checks and return a report dict:
    {soul, d1, dogfood, anti_narration, primer, verdict}

    Each value is a dict with keys {ok: bool, detail: str}.
    verdict is "PASS" iff all 5 are ok, else "FAIL".
    """
    checks = {
        "soul":          lambda: check_soul_conduct_blocks(repo),
        "d1":            lambda: check_skills_d1(repo),
        "dogfood":       lambda: check_dogfood_catalog(repo),
        "anti_narration": lambda: check_anti_narration_selftest(repo),
        "primer":        lambda: check_primer(repo),
    }

    results: dict = {}
    for key, fn in checks.items():
        ok, detail = fn()
        results[key] = {"ok": ok, "detail": detail}

    all_ok = all(v["ok"] for v in results.values())
    results["verdict"] = "PASS" if all_ok else "FAIL"
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# Reporting
# ═══════════════════════════════════════════════════════════════════════════════

_ICONS = {True: "✅", False: "❌"}
_CHECK_LABELS = {
    "soul":          "SOUL conduct blocks",
    "d1":            "Skill D1 compliance",
    "dogfood":       "Dogfood catalog (EX-60/61)",
    "anti_narration": "Anti-narration selftest",
    "primer":        "AGENT-PRIMER.md sections",
}


def print_report(report: dict) -> None:
    """Print an EX-49-style keyless calibration report."""
    verdict = report["verdict"]
    verdict_icon = "✅ PASS" if verdict == "PASS" else "❌ FAIL"

    print()
    print("══════════════════════════════════════════════════════════")
    print("  canvas-calibrate — Keyless Tier (EX-49)                ")
    print("══════════════════════════════════════════════════════════")
    for key, label in _CHECK_LABELS.items():
        entry = report[key]
        icon = _ICONS[entry["ok"]]
        print(f"  {icon} {label}")
        print(f"       {entry['detail']}")
    print("──────────────────────────────────────────────────────────")
    print(f"  Verdict: {verdict_icon}")
    print("══════════════════════════════════════════════════════════")
    print()


# ═══════════════════════════════════════════════════════════════════════════════
# main
# ═══════════════════════════════════════════════════════════════════════════════

def main(argv: list[str]) -> int:
    """
    --refresh : mutating conscientizar then keyless eval
    (no flag)  : non-mutating keyless eval only
    # TODO Task 6: --live  (live LLM tier)
    """
    repo = REPO_ROOT

    if "--live" in argv:
        # TODO Task 6: --live (live LLM tier)
        print("ERROR: --live is not implemented in this task (Task 6).", file=sys.stderr)
        return 2

    if "--refresh" in argv:
        conscientizar(repo)

    report = run_keyless(repo)
    print_report(report)
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
