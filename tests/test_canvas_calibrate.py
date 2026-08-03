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
    assert report["verdict"] in ("PASS", "FAIL")
