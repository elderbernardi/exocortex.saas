"""Schemas e helpers para o coletor de CNPJ."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any


DEFAULT_DATA = {
    "cnpj": None,
    "razao_social": None,
    "nome_fantasia": None,
    "data_abertura": None,
    "capital_social": None,
    "situacao_cadastral": None,
    "cnaes": [],
    "socios": [],
    "filiais": [],
}


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_cnpj(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    if len(digits) != 14:
        raise ValueError("CNPJ deve conter 14 dígitos")
    return digits


def parse_br_date(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value[:19], fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    if len(value) >= 10 and value[4] == "-":
        return value[:10]
    return value


def parse_capital_social(value: Any) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def empty_data(cnpj: str | None = None) -> dict:
    data = dict(DEFAULT_DATA)
    data["cnaes"] = []
    data["socios"] = []
    data["filiais"] = []
    data["cnpj"] = cnpj
    return data


def make_error(code: str, message: str, source: str | None = None) -> dict:
    error = {"code": code, "message": message}
    if source:
        error["source"] = source
    return error


def make_envelope(
    query: str,
    data: dict | None,
    provenance_url: str,
    *,
    method: str = "api",
    raw_cached: bool = False,
    errors: list[dict] | None = None,
    retrieved_at: str | None = None,
) -> dict:
    return {
        "source": "cnpj",
        "query": query,
        "retrieved_at": retrieved_at or now_utc(),
        "data": data or empty_data(query),
        "provenance": {
            "url": provenance_url,
            "method": method,
            "raw_cached": raw_cached,
        },
        "errors": errors or [],
    }
