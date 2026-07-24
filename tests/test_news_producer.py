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
