# tests/test_canvas_calibrate.py
import sys, subprocess
from pathlib import Path
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import canvas_calibrate as CC

def test_keyless_checks_present():
    # the runner exposes the keyless checks as named functions
    for fn in ("check_soul_conduct_blocks", "check_skills_d1", "check_dogfood_catalog",
               "check_anti_narration_selftest", "check_primer"):
        assert hasattr(CC, fn), f"missing keyless check: {fn}"

def test_keyless_run_returns_report():
    report = CC.run_keyless(REPO)
    assert set(report) >= {"soul", "d1", "dogfood", "anti_narration", "primer", "verdict"}
    assert report["verdict"] == "PASS"


# ── Regression tests: I1 (port env) + I2 (health path) ────────────────────────
# These are static source-text assertions — no LLM, no server, no key required.
# They guard against the bugs identified in the F5 Slice A final review:
#   I1: run_live must set HERMES_WEBUI_PORT (not bare PORT) so the isolated server
#       binds :8794 instead of defaulting to :8787 (prod's port).
#   I2: _wait_for_server must poll /health (not /api/health) — the fork routes
#       the plain /health endpoint; /api/health is unrelated.

def _calibrate_source() -> str:
    """Return the full source text of canvas_calibrate.py."""
    src = REPO / "scripts" / "canvas_calibrate.py"
    return src.read_text(encoding="utf-8")

def test_live_uses_hermes_webui_port_not_bare_port():
    """I1 guard: HERMES_WEBUI_PORT must appear; bare PORT= must NOT be set for the server."""
    src = _calibrate_source()
    assert "HERMES_WEBUI_PORT" in src, (
        "run_live must set HERMES_WEBUI_PORT in server_env "
        "(the fork ignores bare PORT and reads HERMES_WEBUI_PORT)"
    )
    # Bare `server_env["PORT"]` would silently be ignored by the fork — forbid it.
    assert 'server_env["PORT"]' not in src, (
        "run_live must NOT set server_env[\"PORT\"]; use HERMES_WEBUI_PORT instead"
    )

def test_wait_for_server_polls_health_not_api_health():
    """I2 guard: _wait_for_server must poll /health, not /api/health."""
    src = _calibrate_source()
    # The code uses f"{base_url}/health" — check that /health appears as a path fragment
    # (without /api/ prefix) somewhere in the _wait_for_server vicinity.
    assert "/health" in src, (
        "_wait_for_server must reference the /health endpoint "
        "(the fork routes /health, not /api/health)"
    )
    # The readiness poll must not target /api/health — that path is not the fork's health route.
    assert '"/api/health"' not in src and "'/api/health'" not in src, (
        "_wait_for_server must not poll /api/health; the fork's health route is /health"
    )
