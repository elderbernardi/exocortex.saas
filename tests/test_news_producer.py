"""Testes do produtor de notícias (excrtx-news-sales-ai, modo auto)."""
from __future__ import annotations
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "excrtx-news-sales-ai"
SCRIPTS = SKILL_DIR / "scripts"
CONFIG = SKILL_DIR / "config" / "noticias.toml"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_load_config_merges_area_defaults():
    cfg = _load("news_config").load_config(str(CONFIG))
    assert cfg["publish"]["default_ttl_days"] == 30
    assert cfg["publish"]["use_docbrain"] is False
    areas = {a["slug"]: a for a in cfg["areas"]}
    assert areas["varejo"]["cadence"] == "weekly"
    assert areas["varejo"]["max_items"] == 3            # override
    assert areas["varejo"]["relevance_threshold"] == 65 # override
    assert areas["limpeza"]["max_items"] == 4           # inherits publish default
    assert areas["limpeza"]["relevance_threshold"] == 60


def test_load_config_rejects_area_without_slug(tmp_path):
    bad = tmp_path / "bad.toml"
    bad.write_text('[[monitored_areas]]\ncadence = "weekly"\n', encoding="utf-8")
    import pytest
    with pytest.raises(ValueError, match="slug"):
        _load("news_config").load_config(str(bad))


def test_cadence_seconds():
    d = _load("news_dispatch")
    assert d.cadence_seconds("daily") == 86400
    assert d.cadence_seconds("weekly") == 604800
    assert d.cadence_seconds("3d") == 3 * 86400
    assert d.cadence_seconds("12h") == 12 * 3600


def test_due_areas_first_run_and_window():
    d = _load("news_dispatch")
    areas = [{"slug": "varejo", "cadence": "weekly"},
             {"slug": "limpeza", "cadence": "daily"}]
    now = 1_000_000_000
    # nunca rodou → ambas vencidas
    assert set(d.due_areas(areas, {}, now)) == {"varejo", "limpeza"}
    # limpeza rodou há 2h (< 1d) → não vence; varejo há 8d → vence
    state = {"varejo": now - 8 * 86400, "limpeza": now - 2 * 3600}
    assert d.due_areas(areas, state, now) == ["varejo"]


def test_mark_run_updates_state():
    d = _load("news_dispatch")
    state = d.mark_run({}, "varejo", 123)
    assert state["varejo"] == 123


def test_classify_new_active_retired():
    g = _load("news_guard")
    assert g.classify(None) == "new"
    assert g.classify({"id": "1", "ativo": True}) == "skip_active"
    assert g.classify({"id": "1", "ativo": False}) == "skip_retired"


def test_partition_macro_keys_on_url_and_null_client():
    g = _load("news_guard")
    candidates = [
        {"url_normalized": "https://a.test/x"},                 # new
        {"url_normalized": "https://b.test/y"},                 # active → skip
        {"url_normalized": "https://c.test/z"},                 # retired → skip
    ]
    existing = {
        ("https://b.test/y", None): {"id": "2", "ativo": True},
        ("https://c.test/z", None): {"id": "3", "ativo": False},
    }
    out = g.partition(candidates, existing)
    assert [c["url_normalized"] for c in out["publish"]] == ["https://a.test/x"]
    assert [c["url_normalized"] for c in out["skip_active"]] == ["https://b.test/y"]
    assert [c["url_normalized"] for c in out["skip_retired"]] == ["https://c.test/z"]


def test_dispatch_cli_lists_due_areas(tmp_path):
    import subprocess, sys
    state = tmp_path / "state.json"
    state.write_text("{}", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "news_dispatch.py"),
         "--config", str(CONFIG), "--state", str(state), "--now", "1000000000"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0
    assert set(proc.stdout.split()) == {"varejo", "limpeza"}  # nunca rodaram
