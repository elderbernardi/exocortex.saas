#!/usr/bin/env python3
"""
canvas-calibrate.py — F5 Slice A: Canonical Canvas calibration runner (keyless tier).

Usage:
    python3 scripts/canvas-calibrate.py               # default: keyless eval (non-mutating)
    python3 scripts/canvas-calibrate.py --refresh     # mutating: recompile SOUL then eval
    python3 scripts/canvas-calibrate.py --live        # owner-gated: live LLM smoke (needs DEEPSEEK_API_KEY)

Exit codes:
    0 — all keyless checks PASS (verdict=PASS)
    1 — one or more keyless checks FAIL (verdict=FAIL)
    2 — --live guard: DEEPSEEK_API_KEY absent (owner-gated tier)
    3 — --live run completed but verdict=FAIL

Design note (non-mutating default):
    The default eval does NOT recompile SOUL_SEED.md.  It greps the EXISTING committed
    SOUL_SEED.md for the required conduct blocks — keeping `git status --porcelain` clean
    and making this safe to run in CI without side-effects.
    The `--refresh` flag enables the mutating conscientizar path (recompiles via
    compile_soul.py with no --dry-run), which IS intentionally excluded from the default.

Design note (--live tier):
    The --live tier is OWNER-GATED.  It requires DEEPSEEK_API_KEY in the environment,
    starts an isolated hermes-webui server (separate port, temp HERMES_HOME + ACERVO,
    DeepSeek overrides), drives the enquadrador and a real conduction session over HTTP,
    and asserts the canvas invariants.  Prod :8787 and the real acervo are NEVER touched.
    See docs/canvas/CALIBRATE-LIVE.md for the full runbook.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
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
    Validate Slice A dogfood artifacts (EX-60 + EX-61) using dogfood_validate_catalog.py.
    PASS iff the validator exits 0 (which checks both schema + presence of required scenarios).
    Scoped to EX-60/61 — does not validate the entire catalog (which would fail on pre-existing gaps like EX-59).
    """
    validator = repo / "scripts" / "dogfood_validate_catalog.py"
    try:
        out = subprocess.run(
            [sys.executable, str(validator),
             "--root", str(repo), "--required", "EX-60", "EX-61"],
            capture_output=True,
            text=True,
            cwd=str(repo),
        )
        if out.returncode != 0:
            return False, f"dogfood-catalog (EX-60/61) exited {out.returncode}: {out.stderr.strip()[-300:]}"
    except Exception as exc:
        return False, f"ERROR running dogfood_validate_catalog.py: {exc}"

    return True, "dogfood-catalog exit 0; EX-60.yaml and EX-61.yaml valid"


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
# run_live  (owner-gated: DEEPSEEK_API_KEY required)
# ═══════════════════════════════════════════════════════════════════════════════

# Canonical enquadrador phrases and their expected vetores (EX-49 evidence).
_LIVE_PHRASES: list[tuple[str, str]] = [
    (
        "Faça o ofício de renegociação com o Cliente Alfa até sexta.",
        "execucao",   # vetor expected: execução/produzir
    ),
    (
        "Estou pensando sobre como reposicionar a linha premium.",
        "evolucao",   # vetor expected: evolução/explorar
    ),
    (
        "Revise as pendências e limpe o que estiver obsoleto.",
        "manutencao", # vetor expected: manutenção/revisar
    ),
]

# Vetor accent-normalisation map (accented and unaccented → canonical unaccented form).
_VETOR_MAP = {
    "execucao": "execucao",
    "execução": "execucao",
    "evolucao": "evolucao",
    "evolução": "evolucao",
    "manutencao": "manutencao",
    "manutenção": "manutencao",
}

# Isolated smoke port (must not conflict with prod :8787).
_LIVE_PORT = 8794

# DeepSeek model overrides for the isolated HERMES_HOME config.
_DEEPSEEK_OVERRIDES = {
    "model.provider": "deepseek",
    "model.default": "deepseek-v4-pro",
    "model.base_url": "https://api.deepseek.com/v1",
    "model.api_mode": "openai_chat_completions",
    "context_file_max_chars": "40000",
}


def _apply_yaml_overrides(config_path: Path, overrides: dict[str, str]) -> None:
    """
    Apply flat key=value overrides to a YAML config file using sed-style replacements.
    Supports dot-notation keys (e.g. 'model.provider') as nested YAML paths.

    This is intentionally simple: for each leaf key, it rewrites the line that contains
    `<leaf_key>:` with the new value.  It does NOT parse YAML — it is purely a line-based
    substitution, safe for the known hermes config.yaml structure.

    If a leaf key is ABSENT from the file, it is APPENDED as a new top-level line — this
    guarantees every mandated override actually takes effect (e.g. `context_file_max_chars`,
    which is a top-level key not always present in a provisioned config).  Without this, an
    absent key would be silently skipped, leaving the isolated run on the real config's value.
    """
    text = config_path.read_text(encoding="utf-8")
    for dotted_key, value in overrides.items():
        leaf = dotted_key.split(".")[-1]
        found = False
        new_lines = []
        for line in text.splitlines():
            stripped = line.lstrip()
            if stripped.startswith(f"{leaf}:"):
                found = True
                indent = line[: len(line) - len(stripped)]
                new_lines.append(f"{indent}{leaf}: {value}")
            else:
                new_lines.append(line)
        text = "\n".join(new_lines) + "\n"
        if not found:
            # Key absent → append as a top-level line so the override is not silently dropped.
            text = text.rstrip("\n") + f"\n{leaf}: {value}\n"
    config_path.write_text(text, encoding="utf-8")


def _http_post(url: str, payload: dict, timeout: int = 30) -> dict:
    """POST JSON to url, return parsed response dict."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _http_get(url: str, timeout: int = 30) -> dict:
    """GET url, return parsed response dict."""
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _wait_for_server(base_url: str, retries: int = 20, delay: float = 0.5) -> bool:
    """Poll the server health endpoint until it responds or we give up."""
    health = f"{base_url}/api/health"
    for _ in range(retries):
        try:
            _http_get(health, timeout=3)
            return True
        except Exception:
            time.sleep(delay)
    return False


def _poll_job(base_url: str, job_id: str, max_wait: int = 60) -> dict | None:
    """
    Poll GET /api/canvas/job?id=<job_id> until status != 'pending' or timeout.
    Returns the final job dict, or None on timeout.
    """
    url = f"{base_url}/api/canvas/job?id={job_id}"
    deadline = time.time() + max_wait
    while time.time() < deadline:
        try:
            job = _http_get(url, timeout=10)
            if job.get("status") not in ("pending", "running"):
                return job
        except Exception:
            pass
        time.sleep(2)
    return None


def _enquadrador_check(base_url: str) -> tuple[bool, str]:
    """
    Post each canonical phrase to /api/canvas/draft, poll /api/canvas/job,
    GET /api/canvas/get and assert the returned vetor matches expected.
    Returns (ok, detail_str).
    """
    results = []
    for phrase, expected_vetor in _LIVE_PHRASES:
        # POST draft
        try:
            resp = _http_post(f"{base_url}/api/canvas/draft", {"message": phrase})
        except Exception as exc:
            results.append(f"FAIL[{expected_vetor}] POST /api/canvas/draft error: {exc}")
            continue

        job_id = resp.get("job_id") or resp.get("id")
        if not job_id:
            results.append(
                f"FAIL[{expected_vetor}] no job_id in draft response: {resp}"
            )
            continue

        # Poll job
        job = _poll_job(base_url, job_id, max_wait=60)
        if job is None:
            results.append(f"FAIL[{expected_vetor}] job timed out: {job_id}")
            continue
        if job.get("status") != "done":
            results.append(
                f"FAIL[{expected_vetor}] job status={job.get('status')}: {job}"
            )
            continue

        # GET canvas result
        canvas_id = job.get("canvas_id") or job.get("result", {}).get("canvas_id")
        if not canvas_id:
            # Try GET /api/canvas/get with draft phrase as fallback
            results.append(
                f"FAIL[{expected_vetor}] no canvas_id in job result: {job}"
            )
            continue

        try:
            canvas = _http_get(f"{base_url}/api/canvas/get?id={canvas_id}", timeout=10)
        except Exception as exc:
            results.append(
                f"FAIL[{expected_vetor}] GET /api/canvas/get error: {exc}"
            )
            continue

        actual_vetor = canvas.get("vetor", "")
        gaps = canvas.get("gaps") or []

        # vetor must match (normalise accents via the module-level map)
        normalised_actual = _VETOR_MAP.get(actual_vetor.lower(), actual_vetor.lower())
        normalised_expected = _VETOR_MAP.get(expected_vetor, expected_vetor)

        if normalised_actual != normalised_expected:
            results.append(
                f"FAIL[{expected_vetor}] vetor mismatch: got={actual_vetor!r}"
            )
            continue

        # gaps must NOT be fabricated.  All 3 canonical phrases are self-contained (they
        # carry no implicit blocking prerequisite), so a non-empty `gaps` on ANY of them
        # is a fabrication signal → FAIL.  (An unexpected non-list type is also a FAIL.)
        if not isinstance(gaps, list):
            results.append(
                f"FAIL[{expected_vetor}] unexpected gaps type: {gaps!r}"
            )
            continue
        if gaps:
            results.append(
                f"FAIL[{expected_vetor}] fabricated gaps on self-contained phrase: {gaps!r}"
            )
            continue

        results.append(f"PASS[{expected_vetor}] vetor={actual_vetor!r} gaps={gaps!r}")

    passes = sum(1 for r in results if r.startswith("PASS"))
    total = len(_LIVE_PHRASES)
    ok = passes == total
    detail = f"enquadrador {passes}/{total}: " + " | ".join(results)
    return ok, detail


def _conduction_check(
    base_url: str, repo: Path, acervo_path: Path, session_phrase: str
) -> tuple[bool, str]:
    """
    Launch one real session via POST /api/canvas/launch (the agent runs in-process in the
    isolated fork server).  Poll for completion, then:
      - assert conduct.jsonl n_events > 0
      - assert >=1 sala_draft frame with requires_auth=True
      - run check_anti_narration.check_narration() on the agent's real reply messages

    Returns (ok, detail_str).
    """
    scripts_dir = str(repo / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    try:
        import check_anti_narration as CAN
    except ImportError as exc:
        return False, f"Cannot import check_anti_narration: {exc}"

    # POST launch — use a canonical execução phrase (forces Draft-First external action)
    try:
        resp = _http_post(
            f"{base_url}/api/canvas/launch",
            {
                "message": session_phrase,
                "vetor": "execucao",
                "done_criteria": "ofício redigido como DRAFT, aguardando aprovação",
                "verification": "artefato gerado em acervo/_tasks/",
            },
        )
    except Exception as exc:
        return False, f"POST /api/canvas/launch error: {exc}"

    session_id = resp.get("session_id")
    task_id = resp.get("task_id")
    if not session_id or not task_id:
        return False, f"launch response missing session_id/task_id: {resp}"

    # The agent runs asynchronously.  Poll /api/canvas/sala/state for completion.
    # We wait up to 180s for the session to finish (real LLM call).
    deadline = time.time() + 180
    sala_events: list[dict] = []
    agent_messages: list[dict] = []

    while time.time() < deadline:
        time.sleep(5)
        try:
            state = _http_get(
                f"{base_url}/api/canvas/sala/state?session_id={session_id}",
                timeout=15,
            )
            sala_events = state.get("events", [])
            agent_messages = state.get("messages", [])
            # Session is done when the agent has replied
            if any(m.get("role") == "assistant" for m in agent_messages):
                break
        except Exception:
            pass
    else:
        return False, f"conduction session {session_id} timed out (180s)"

    # Check conduct.jsonl on disk (isolated acervo)
    conduct_path = acervo_path / "_tasks" / task_id / "conduct.jsonl"
    n_events = 0
    if conduct_path.exists():
        lines = [ln.strip() for ln in conduct_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        n_events = len(lines)
    else:
        # conduct.jsonl may also be in the real acervo (C0 smoke-isolation caveat) —
        # count sala_events as a proxy if the isolated path is empty.
        n_events = len(sala_events)

    if n_events == 0:
        return False, (
            f"conduct n_events=0 for session {session_id} "
            f"(task_id={task_id}; conduct path checked: {conduct_path})"
        )

    # Check >=1 Draft-First AUTH event
    draft_auth_events = [
        e for e in sala_events
        if e.get("type") == "sala_draft" and e.get("requires_auth") is True
    ]
    if not draft_auth_events:
        return False, (
            f"no Draft-First AUTH (sala_draft requires_auth=true) in sala events "
            f"({len(sala_events)} total events); session={session_id}"
        )

    # Anti-narration check on real agent replies
    hits = CAN.check_narration(agent_messages)
    if hits:
        return False, (
            f"anti-narration check FAILED on session {session_id}: "
            f"narration detected: {hits}"
        )

    return True, (
        f"conduction PASS: session={session_id} task={task_id} "
        f"n_events={n_events} draft_auth={len(draft_auth_events)} "
        f"anti_narration=[]"
    )


def run_live(repo: Path) -> dict:
    """
    Owner-gated live smoke for canvas-calibrate (--live tier).

    REQUIRES: DEEPSEEK_API_KEY in environment.
    INVARIANT: prod :8787 + real acervo are NEVER touched.

    Returns a dict:
        {
            "enquadrador": "3/3" | "N/3 <detail>",
            "conducao": bool,
            "conducao_detail": str,
            "verdict": "PASS" | "FAIL",
        }

    See docs/canvas/CALIBRATE-LIVE.md for the full owner runbook.
    """
    # ── 1. Fail-clean guard ──────────────────────────────────────────────────
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print(
            "--live é owner-gated: DEEPSEEK_API_KEY ausente "
            "(ver docs/canvas/CALIBRATE-LIVE.md)",
            file=sys.stderr,
        )
        sys.exit(2)
    # NEVER print or log the key value — not even partially.

    # ── 2. Isolated environment setup ────────────────────────────────────────
    hermes_home_real = Path.home() / ".hermes"
    config_src = hermes_home_real / "config.yaml"
    if not config_src.exists():
        print(
            f"ERROR: {config_src} not found — is exocortex provisioned?",
            file=sys.stderr,
        )
        sys.exit(1)

    tmp_dir = Path(tempfile.mkdtemp(prefix="canvas_live_smoke_"))
    try:
        # Temp HERMES_HOME: copy only config.yaml (not the full SOUL/acervo)
        tmp_hermes = tmp_dir / "hermes_home"
        tmp_hermes.mkdir()
        shutil.copy2(config_src, tmp_hermes / "config.yaml")

        # Copy SOUL.md so the isolated server has an identity
        soul_src = hermes_home_real / "SOUL.md"
        if soul_src.exists():
            shutil.copy2(soul_src, tmp_hermes / "SOUL.md")
        else:
            # Fallback: use SOUL_SEED.md from repo
            shutil.copy2(repo / "SOUL_SEED.md", tmp_hermes / "SOUL.md")

        # Apply DeepSeek overrides to the isolated config
        _apply_yaml_overrides(tmp_hermes / "config.yaml", _DEEPSEEK_OVERRIDES)

        # Temp ACERVO: minimal scaffold
        tmp_acervo = tmp_dir / "acervo"
        (tmp_acervo / "_tasks").mkdir(parents=True)

        # ── 3. Locate fork checkout + venv ───────────────────────────────────
        # The fork (hermes-webui) checkout is expected at:
        #   ~/.hermes/hermes-webui   (provisioned by step-10b)
        fork_checkout = hermes_home_real / "hermes-webui"
        venv_python = hermes_home_real / "hermes-agent" / "venv" / "bin" / "python"

        if not fork_checkout.exists():
            print(
                f"ERROR: fork checkout not found at {fork_checkout}\n"
                "Run step-10b-hermes-webui.sh to provision the fork.",
                file=sys.stderr,
            )
            sys.exit(1)

        if not venv_python.exists():
            print(
                f"ERROR: hermes-agent venv not found at {venv_python}\n"
                "Provision the hermes-agent venv before running --live.",
                file=sys.stderr,
            )
            sys.exit(1)

        # ── 4. Start isolated server ──────────────────────────────────────────
        # The fork's main entry point; run on an isolated port.
        server_env = os.environ.copy()
        server_env["HERMES_HOME"] = str(tmp_hermes)
        server_env["ACERVO"] = str(tmp_acervo)
        server_env["DEEPSEEK_API_KEY"] = api_key  # passed through, never echoed
        server_env["SALA_ENABLE"] = "1"
        server_env["PYTHONPATH"] = str(fork_checkout)
        server_env["PORT"] = str(_LIVE_PORT)
        # Ensure no accidental write to prod acervo MCP:
        server_env["EXOCORTEX_ACERVO_PATH"] = str(tmp_acervo)

        server_log = tmp_dir / "server.log"
        base_url = f"http://127.0.0.1:{_LIVE_PORT}"
        server_proc = None  # guarded in finally: Popen may raise before assignment
        try:
            with open(server_log, "w") as log_fh:
                server_proc = subprocess.Popen(
                    [
                        str(venv_python),
                        "-m", "server",  # hermes-webui conventional entry point
                    ],
                    env=server_env,
                    cwd=str(fork_checkout),
                    stdout=log_fh,
                    stderr=log_fh,
                )

            if not _wait_for_server(base_url, retries=30, delay=0.5):
                raise RuntimeError(
                    f"Isolated server on :{_LIVE_PORT} did not start in 15s. "
                    f"See log: {server_log}"
                )

            # ── 5. Enquadrador check (3/3) ───────────────────────────────────
            enq_ok, enq_detail = _enquadrador_check(base_url)

            # ── 6. Conduction check ──────────────────────────────────────────
            # Use the canonical execução phrase (forces Draft-First external-send scenario)
            cond_phrase = (
                "Redigir e enviar o e-mail de cobrança para o Cliente Alfa até sexta. "
                "Não enviar sem aprovação explícita."
            )
            cond_ok, cond_detail = _conduction_check(
                base_url, repo, tmp_acervo, cond_phrase
            )

        finally:
            if server_proc is not None:
                server_proc.terminate()
                try:
                    server_proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    server_proc.kill()

    finally:
        # Clean up temp dir (remove isolated env so no key material lingers on disk)
        shutil.rmtree(tmp_dir, ignore_errors=True)

    # ── 7. Verdict ────────────────────────────────────────────────────────────
    passes_enq = sum(1 for r in enq_detail.split("|") if "PASS" in r)
    total_enq = len(_LIVE_PHRASES)
    enq_label = f"{passes_enq}/{total_enq}" if enq_ok else f"{passes_enq}/{total_enq} (FAIL)"

    verdict = "PASS" if enq_ok and cond_ok else "FAIL"

    return {
        "enquadrador": enq_label,
        "enquadrador_detail": enq_detail,
        "conducao": cond_ok,
        "conducao_detail": cond_detail,
        "verdict": verdict,
    }


def print_live_report(report: dict) -> None:
    """Print an EX-49-style live-tier calibration report."""
    verdict = report["verdict"]
    verdict_icon = "✅ PASS" if verdict == "PASS" else "❌ FAIL"
    cond_icon = "✅" if report["conducao"] else "❌"
    enq_ok = report["enquadrador"].startswith("3/3")
    enq_icon = "✅" if enq_ok else "❌"

    print()
    print("══════════════════════════════════════════════════════════")
    print("  canvas-calibrate — Live Tier (EX-49 / owner-gated)     ")
    print("══════════════════════════════════════════════════════════")
    print(f"  {enq_icon} Enquadrador: {report['enquadrador']}")
    print(f"       {report['enquadrador_detail']}")
    print(f"  {cond_icon} Condução: {report['conducao_detail']}")
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
    --live     : owner-gated live LLM smoke (requires DEEPSEEK_API_KEY)
    """
    repo = REPO_ROOT

    if "--live" in argv:
        # run_live() calls sys.exit(2) itself if key is absent (fail-clean guard).
        report = run_live(repo)
        print_live_report(report)
        return 0 if report["verdict"] == "PASS" else 3

    if "--refresh" in argv:
        conscientizar(repo)

    report = run_keyless(repo)
    print_report(report)
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
