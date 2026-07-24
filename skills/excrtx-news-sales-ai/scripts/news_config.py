"""Carrega e valida a config do produtor de notícias (TOML)."""
from __future__ import annotations
import tomllib
from typing import Any

_PUBLISH_DEFAULTS = {
    "default_escopo": "macro",
    "default_ttl_days": 30,
    "max_items_per_run": 4,
    "relevance_threshold": 60,
    "use_docbrain": False,
}


def load_config(path: str) -> dict[str, Any]:
    with open(path, "rb") as fh:
        raw = tomllib.load(fh)
    publish = {**_PUBLISH_DEFAULTS, **raw.get("publish", {})}
    areas: list[dict[str, Any]] = []
    for entry in raw.get("monitored_areas", []):
        slug = entry.get("slug")
        if not slug:
            raise ValueError("monitored_areas entry missing required 'slug'")
        areas.append({
            "slug": slug,
            "cadence": entry.get("cadence", "weekly"),
            "max_items": entry.get("max_items", publish["max_items_per_run"]),
            "relevance_threshold": entry.get(
                "relevance_threshold", publish["relevance_threshold"]),
        })
    return {"publish": publish, "areas": areas}
