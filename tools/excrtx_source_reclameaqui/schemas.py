"""Schemas e helpers para o coletor de Reclame Aqui."""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone
from typing import Any


# --- Canonical data shape for RA company profile ---

DEFAULT_DATA = {
    "empresa": None,
    "slug": None,
    "nota_geral": None,
    "total_reclamacoes": None,
    "respondidas": None,
    "taxa_resolucao": None,
    "tempo_medio_resposta": None,
    "categorias_problema": [],
    "reclamacoes": [],
    "serie_temporal": {},
}


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify_query(value: str) -> str:
    """Convert a company name or URL fragment into a Reclame Aqui slug.

    Examples:
        "Girando Sol" -> "girando-sol"
        "/empresa/girando-sol/" -> "girando-sol"
        "https://www.reclameaqui.com.br/empresa/girando-sol/" -> "girando-sol"
    """
    if not value:
        return ""

    # If it looks like a URL, extract the last path segment
    if "/" in value:
        # Strip protocol and domain, keep path
        path = re.sub(r"https?://[^/]+", "", value).strip("/")
        # Extract slug from /empresa/<slug>/ or /<slug>/
        parts = [p for p in path.split("/") if p]
        if "empresa" in parts:
            idx = parts.index("empresa")
            if idx + 1 < len(parts):
                value = parts[idx + 1]
            else:
                value = parts[-1] if parts else ""
        else:
            value = parts[-1] if parts else ""

    # Normalize: lowercase, strip accents, replace non-alnum with hyphen
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value


def make_error(code: str, message: str, source: str | None = None) -> dict:
    error: dict[str, Any] = {"code": code, "message": message}
    if source:
        error["source"] = source
    return error


def make_envelope(
    query: str,
    data: dict | None,
    provenance_url: str,
    *,
    method: str = "html",
    raw_cached: bool = False,
    errors: list[dict] | None = None,
    retrieved_at: str | None = None,
) -> dict:
    return {
        "source": "reclameaqui",
        "query": query,
        "retrieved_at": retrieved_at or now_utc(),
        "data": data or empty_data(),
        "provenance": {
            "url": provenance_url,
            "method": method,
            "raw_cached": raw_cached,
        },
        "errors": errors or [],
    }


def empty_data() -> dict:
    data = dict(DEFAULT_DATA)
    data["categorias_problema"] = []
    data["reclamacoes"] = []
    data["serie_temporal"] = {}
    return data


# --- Parsing helpers ---

def parse_float(value: str | int | float | None) -> float | None:
    """Parse a numeric string that may use comma as decimal separator."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace("%", "").strip()
    if not text or text == "--":
        return None
    text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def parse_int(value: str | int | None) -> int | None:
    """Parse an integer from string, handling dots as thousand separators."""
    if value is None:
        return None
    if isinstance(value, int):
        return value
    text = str(value).strip().replace(".", "").replace(",", "")
    text = re.sub(r"[^\d-]", "", text)
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def parse_number_or_dash(value: str | int | float | None) -> float | int | None:
    """Parse a value that might be a number or '--' (RA's placeholder for no data)."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return value
    text = str(value).strip()
    if not text or text == "--":
        return None
    return parse_float(text)


def parse_percentage(value: str | int | float | None) -> float | None:
    """Parse percentages like '87%' or fractional strings like '0.87'."""
    parsed = parse_float(value)
    if parsed is None:
        return None
    if parsed > 1:
        return parsed / 100
    return parsed


def parse_java_object_string(value: str | None) -> dict[str, str]:
    """Parse a Java .toString() style string like '{key1=val1, key2=val2}'.

    RA stores companyIndex6Months as a Java object toString representation.
    """
    if not value or not value.strip().startswith("{"):
        return {}
    text = value.strip()
    # Remove outer braces
    text = text.strip("{}")
    result: dict[str, str] = {}
    # Simple split by comma, then by = — works for flat string values
    for pair in text.split(", "):
        if "=" in pair:
            k, v = pair.split("=", 1)
            result[k.strip()] = v.strip()
    return result
