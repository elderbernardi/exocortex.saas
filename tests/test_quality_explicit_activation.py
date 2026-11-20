"""Opt-in contracts for both editorial skills; production does not depend on loading them."""
from pathlib import Path

import pytest
import yaml

from scripts.exocortex_runtime_guard import enforce_skill_gate

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


@pytest.mark.parametrize("name", ["excrtx-quality-antislop", "excrtx-quality-gate"])
def test_opt_in_visible_before_loading_and_in_always_loaded_rules(name):
    _, header, body = (SKILLS / name / "SKILL.md").read_text().split("---", 2)
    meta = yaml.safe_load(header)
    when = body.split("## When to Use", 1)[1].split("\n## ", 1)[0]
    for surface in (meta["description"], meta["compiled_rules"].lstrip().splitlines()[0], when):
        assert "explicit" in surface.lower(), name
    assert "mention" in when.lower()
    assert "current" in when.lower()
    for case in meta["metadata"]["hermes"]["calibration"]:
        assert name in case["test_prompt"], case["feature_id"]


@pytest.mark.parametrize("name", ["excrtx-produce-artifacts", "excrtx-produce-oficios", "excrtx-produce-slides"])
def test_production_can_run_without_quality_skills_but_keeps_budget(name):
    check = enforce_skill_gate(name, loaded_skills=[], estimated_context_tokens=1, skills_dir=SKILLS)
    assert check["allowed"], check
    exceeded = enforce_skill_gate(name, [], check["gate"]["max_context_tokens"] + 1, skills_dir=SKILLS)
    assert exceeded["reason"] == "context_budget_exceeded"


def test_skills_are_available_on_demand_not_preloaded_by_default():
    bundle = yaml.safe_load((ROOT / "skill-bundles/exocortex-alpha.yaml").read_text())
    for name in ("excrtx-quality-antislop", "excrtx-quality-gate"):
        assert name not in bundle["skills"]
        assert (SKILLS / name / "SKILL.md").is_file()


def test_mixed_route_does_not_imply_a_prose_review_or_score():
    gate = (SKILLS / "excrtx-quality-gate" / "SKILL.md").read_text()
    entry = next(line for line in gate.splitlines() if line.startswith("| **MIXED**"))
    assert "if requested" in entry.lower()
    anti = (SKILLS / "excrtx-quality-antislop" / "SKILL.md").read_text()
    assert "does not start the unified gate" in anti


def test_seed_no_longer_scores_every_delivery():
    defaults = (ROOT / "SOUL_SEED.md").read_text().split("<!-- COMPILED_RULES_START -->")[0]
    assert "Toda prosa gerada passa pelo crivo" not in defaults
    assert "pedido expresso" in defaults.split("## Anti-Slop (Textual)")[1].split("## Anti-Slop (Visual)")[0]
