"""Schemas e helpers para o coletor de Google Trends."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any


def ts_to_partial(value: str) -> str:
    """Convert YYYY-MM-DD to YYYY-MM (daily granularity output from Trends)."""
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return value[:7]
    return value


DEFAULT_DATA = {
    "termos": [],
    "serie_temporal": {},
    "interesse_por_regiao": {},
    "queries_relacionadas": {},
}


def today_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_term(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def decode_period(period: str | None) -> str:
    """Convert user-friendly period aliases to Google Trends format.

    Accepted:
      - '7d', '1m', '3m', '12m', '5y'
      - 'YYYY-MM-DD YYYY-MM-DD' (range)
      - default: 'today 5-Y' (last 5 years, daily)
    """
    if not period:
        return "today 5-Y"
    period = period.strip().lower()
    aliases = {
        "1d": "today 1-d",
        "7d": "today 7-d",
        "30d": "today 1-m",
        "1m": "today 1-m",
        "3m": "today 3-m",
        "6m": "today 6-m",
        "12m": "today 12-m",
        "5y": "today 5-y",
    }
    if period in aliases:
        return aliases[period]
    parts = period.split()
    if len(parts) == 2 and all(re.match(r"\d{4}-\d{2}-\d{2}", p) for p in parts):
        return f"{parts[0]} {parts[1]}"
    return "today 5-Y"


def parse_period(value: str) -> dict:
    """Convert a period string to start_date / end_date dict."""
    formatted = decode_period(value)
    parts = formatted.split(" ", 1)
    if len(parts) == 2:
        kind, detail = parts
        now = datetime.now()
        if kind == "today":
            unit_d = detail.split("-")
            n = int(unit_d[0]) if unit_d[0].isdigit() else 1
            u = unit_d[-1]
            end = now
            if u == "d":
                start = __import__("datetime").date(now.year, now.month, now.day)
                start = end.replace(day=max(1, end.day - n + 1))
                return {"start": start.strftime("%Y-%m-%d"), "end": end.strftime("%Y-%m-%d")}
            if u == "m":
                m2 = end.month - n
                y = end.year
                while m2 <= 0:
                    m2 += 12
                    y -= 1
                return {
                    "start": f"{y}-{m2:02d}-01",
                    "end": end.strftime("%Y-%m-%d"),
                }
            if u == "y":
                return {
                    "start": f"{end.year - n}-01-01",
                    "end": end.strftime("%Y-%m-%d"),
                }
        else:
            return {"start": parts[0], "end": parts[1]}
    return {"start": None, "end": None}


def empty_data(terms: list[str] | None = None) -> dict:
    data = dict(DEFAULT_DATA)
    data["termos"] = terms or []
    data["serie_temporal"] = {}
    data["interesse_por_regiao"] = {}
    data["queries_relacionadas"] = {}
    return data


def make_error(code: str, message: str, source: str | None = None) -> dict:
    error = {"code": code, "message": message}
    if source:
        error["source"] = source
    return error


def make_envelope(
    query: str,
    data: dict[str, Any] | None,
    provenance_url: str,
    *,
    method: str = "api",
    raw_cached: bool = False,
    errors: list[dict] | None = None,
    retrieved_at: str | None = None,
    provenance_extra: dict[str, Any] | None = None,
) -> dict:
    prov = {"url": provenance_url, "method": method, "raw_cached": raw_cached}
    if provenance_extra:
        prov.update(provenance_extra)
    return {
        "source": "google_trends",
        "query": query,
        "retrieved_at": retrieved_at or today_utc(),
        "data": data or empty_data(),
        "provenance": prov,
        "errors": errors or [],
    }
