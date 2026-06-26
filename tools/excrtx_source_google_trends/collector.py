"""Coletor de dados de Google Trends via endpoints públicos do trends.google.com."""

from __future__ import annotations

import json
import re
import urllib.parse
from datetime import datetime, timezone
from typing import Any

import httpx

from .schemas import decode_period, empty_data, make_envelope, make_error, normalize_term

USER_AGENT = "exocortex-google-trends-collector/1.0"
BASE_TRENDS_URL = "https://trends.google.com/trends"
EXPLORE_URL = f"{BASE_TRENDS_URL}/api/explore"
INTEREST_OVER_TIME_URL = f"{BASE_TRENDS_URL}/api/widgetdata/multiline"
INTEREST_BY_REGION_URL = f"{BASE_TRENDS_URL}/api/widgetdata/comparedgeo"
RELATED_QUERIES_URL = f"{BASE_TRENDS_URL}/api/widgetdata/relatedsearches"
AUTOCOMPLETE_URL = f"{BASE_TRENDS_URL}/api/autocomplete"


def _safe_float(value: str | int | float | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = str(value).replace(",", ".").replace("%", "").strip()
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def _decode_json_body(response: httpx.Response) -> dict | list | None:
    text = response.text.lstrip()
    if text.startswith(")]}',"):
        text = text[5:].lstrip("\n\r")
    elif text.startswith(")]}'"):
        text = text[4:].lstrip("\n\r,")
    if not text:
        return None
    return json.loads(text)


def _point_month(entry: dict[str, Any]) -> str | None:
    ts = entry.get("time")
    if ts:
        try:
            return datetime.fromtimestamp(int(str(ts)), tz=timezone.utc).strftime("%Y-%m")
        except (TypeError, ValueError, OSError):
            pass
    raw = str(entry.get("date") or entry.get("formattedTime") or entry.get("formattedAxisTime") or "").strip()
    if not raw:
        return None
    if len(raw) >= 7 and raw[:4].isdigit() and raw[4] == "-":
        return raw[:7]
    normalized = raw.lower().replace(".", "").replace("  ", " ")
    month_map = {
        "jan": "01", "january": "01", "janeiro": "01",
        "feb": "02", "fev": "02", "february": "02", "fevereiro": "02",
        "mar": "03", "march": "03", "março": "03", "marco": "03",
        "apr": "04", "abr": "04", "april": "04", "abril": "04",
        "may": "05", "mai": "05", "maio": "05",
        "jun": "06", "june": "06", "junho": "06",
        "jul": "07", "july": "07", "julho": "07",
        "aug": "08", "ago": "08", "august": "08", "agosto": "08",
        "sep": "09", "set": "09", "september": "09", "setembro": "09",
        "oct": "10", "out": "10", "october": "10", "outubro": "10",
        "nov": "11", "november": "11", "novembro": "11",
        "dec": "12", "dez": "12", "december": "12", "dezembro": "12",
    }
    match = re.search(r"([a-zç]+)\s+(\d{4})", normalized)
    if match:
        month = month_map.get(match.group(1))
        if month:
            return f"{match.group(2)}-{month}"
    return raw


class GoogleTrendsCollector:
    def __init__(
        self,
        *,
        timeout_seconds: float = 15.0,
        transport: httpx.BaseTransport | None = None,
        user_agent: str = USER_AGENT,
        locale: str = "pt-BR",
        geo: str = "BR",
    ):
        self.timeout_seconds = timeout_seconds
        self.transport = transport
        self.user_agent = user_agent
        self.locale = locale
        self.geo = geo

    def _client(self) -> httpx.Client:
        return httpx.Client(
            timeout=self.timeout_seconds,
            headers={
                "User-Agent": self.user_agent,
                "Accept": "application/json,text/javascript,*/*;q=0.1",
                "Accept-Language": self.locale,
            },
            transport=self.transport,
            follow_redirects=True,
        )

    def _request_json(
        self,
        client: httpx.Client,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> tuple[dict | list | None, dict | None]:
        try:
            response = client.request(method, url, params=params)
        except httpx.TimeoutException:
            return None, make_error("timeout", f"Timeout consultando {url}", "googletrends")
        except httpx.HTTPError as exc:
            return None, make_error("network_error", str(exc), "googletrends")

        if response.status_code == 429:
            return None, make_error("rate_limited", "Rate limit do Google Trends atingido", "googletrends")
        if response.status_code >= 400:
            return None, make_error("http_error", f"HTTP {response.status_code} em Google Trends", "googletrends")

        try:
            return _decode_json_body(response), None
        except (ValueError, json.JSONDecodeError):
            return None, make_error("invalid_json", "Resposta inválida do Google Trends", "googletrends")

    def _bootstrap_cookie(self, client: httpx.Client, geo: str) -> dict | None:
        if self.transport is not None:
            return None
        try:
            client.get(f"{BASE_TRENDS_URL}/explore/?geo={geo}")
        except httpx.TimeoutException:
            return make_error("timeout", "Timeout inicializando cookie do Google Trends", "googletrends")
        except httpx.HTTPError as exc:
            return make_error("network_error", str(exc), "googletrends")
        return None

    def autocomplete(self, query: str) -> list[str]:
        term = normalize_term(query)
        if not term:
            return []
        with self._client() as client:
            cookie_error = self._bootstrap_cookie(client, self.geo)
            if cookie_error:
                return []
            payload, err = self._request_json(
                client,
                "GET",
                f"{AUTOCOMPLETE_URL}/{urllib.parse.quote(term)}",
                params={"hl": self.locale, "geo": self.geo},
            )
        if err or not payload:
            return []
        if isinstance(payload, list) and len(payload) >= 2 and isinstance(payload[1], list):
            return [str(item) for item in payload[1][:10]]
        if isinstance(payload, dict):
            default = payload.get("default")
            if isinstance(default, list):
                out: list[str] = []
                for item in default[:10]:
                    if isinstance(item, dict):
                        out.append(str(item.get("query") or item.get("title") or ""))
                    elif item:
                        out.append(str(item))
                return [item for item in out if item]
        return []

    def _fetch_widgets(
        self,
        client: httpx.Client,
        terms: list[str],
        period: str,
        geo: str,
        category: int,
    ) -> tuple[list[dict[str, Any]] | None, list[dict]]:
        cookie_error = self._bootstrap_cookie(client, geo)
        if cookie_error:
            return None, [cookie_error]

        req_payload = {
            "comparisonItem": [{"keyword": term, "geo": geo, "time": period} for term in terms],
            "category": category,
            "property": "",
        }
        payload, err = self._request_json(
            client,
            "POST",
            EXPLORE_URL,
            params={"hl": self.locale, "tz": "-180", "req": json.dumps(req_payload)},
        )
        if err:
            return None, [err]
        if not isinstance(payload, dict):
            return None, [make_error("invalid_json", "Payload explore inesperado", "googletrends")]
        widgets = payload.get("widgets")
        if isinstance(widgets, list):
            return widgets, []
        if isinstance(payload.get("default"), dict):
            default_payload = payload["default"]
            return [
                {"id": "TIMESERIES", "data": default_payload},
                {"id": "GEO_MAP", "data": default_payload},
                {"id": "RELATED_QUERIES", "data": default_payload},
            ], []
        return None, [make_error("invalid_json", "Resposta explore sem widgets", "googletrends")]

    def _fetch_widget_payload(
        self,
        client: httpx.Client,
        endpoint: str,
        widget: dict[str, Any],
    ) -> tuple[dict | list | None, dict | None]:
        request_payload = widget.get("request")
        token = widget.get("token")
        if not request_payload or not token:
            return None, make_error("invalid_widget", "Widget sem request/token", "googletrends")
        return self._request_json(
            client,
            "GET",
            endpoint,
            params={
                "hl": self.locale,
                "tz": "-180",
                "req": json.dumps(request_payload),
                "token": token,
            },
        )

    def explore(
        self,
        terms: list[str],
        period: str = "today 5-Y",
        geo: str = "BR",
        category: int = 0,
    ) -> tuple[dict, list[dict]]:
        clean_terms = [normalize_term(term) for term in terms if normalize_term(term)]
        if not clean_terms:
            return empty_data([]), []

        result = empty_data(clean_terms)
        errors: list[dict] = []
        period_str = decode_period(period)

        with self._client() as client:
            widgets, widget_errors = self._fetch_widgets(client, clean_terms, period_str, geo, category)
            if widget_errors:
                return result, widget_errors
            assert widgets is not None

            related_done = False
            for widget in widgets:
                if not isinstance(widget, dict):
                    continue
                widget_id = str(widget.get("id") or "")

                # Test doubles may already embed data in the widget itself.
                if isinstance(widget.get("data"), dict):
                    self._parse_widget_payload(widget_id, widget["data"], result, clean_terms)
                    if "RELATED_QUERIES" in widget_id:
                        related_done = True
                    continue

                if widget_id == "TIMESERIES":
                    payload, err = self._fetch_widget_payload(client, INTEREST_OVER_TIME_URL, widget)
                    if err:
                        errors.append(err)
                    else:
                        self._parse_timeseries_payload(payload, result, clean_terms)
                elif widget_id == "GEO_MAP":
                    payload, err = self._fetch_widget_payload(client, INTEREST_BY_REGION_URL, widget)
                    if err:
                        errors.append(err)
                    else:
                        self._parse_geo_payload(payload, result, clean_terms)
                elif "RELATED_QUERIES" in widget_id and not related_done:
                    payload, err = self._fetch_widget_payload(client, RELATED_QUERIES_URL, widget)
                    if err:
                        errors.append(err)
                    else:
                        self._parse_related_payload(payload, result, clean_terms)
                    related_done = True

        return result, errors

    def _parse_widget_payload(self, widget_id: str, payload: dict[str, Any], result: dict, terms: list[str]) -> None:
        if widget_id == "TIMESERIES":
            self._parse_timeseries_payload(payload, result, terms)
        elif widget_id == "GEO_MAP":
            self._parse_geo_payload(payload, result, terms)
        elif "RELATED_QUERIES" in widget_id:
            self._parse_related_payload(payload, result, terms)

    def _parse_timeseries_payload(self, payload: Any, result: dict, terms: list[str]) -> None:
        data = payload.get("default", payload) if isinstance(payload, dict) else {}
        entries = data.get("timelineData", []) if isinstance(data, dict) else []
        if not isinstance(entries, list):
            return
        monthly: dict[str, dict[str, list[float]]] = {term: {} for term in terms}
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            month = _point_month(entry)
            if not month:
                continue
            values = entry.get("value", [])
            if not isinstance(values, list):
                continue
            for idx, value in enumerate(values):
                if idx >= len(terms):
                    continue
                numeric = _safe_float(value)
                if numeric is None:
                    continue
                term = terms[idx]
                monthly.setdefault(term, {}).setdefault(month, []).append(numeric)

        for term in terms:
            result["serie_temporal"][term] = [
                {"date": month, "value": round(sum(samples) / len(samples), 2)}
                for month, samples in sorted(monthly.get(term, {}).items())
                if samples
            ]

    def _parse_geo_payload(self, payload: Any, result: dict, terms: list[str]) -> None:
        data = payload.get("default", payload) if isinstance(payload, dict) else {}
        entries = data.get("geoMapData", []) if isinstance(data, dict) else []
        if not isinstance(entries, list):
            return
        for term in terms:
            result["interesse_por_regiao"].setdefault(term, {})
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            children = entry.get("children") or entry.get("containedGeo")
            if isinstance(children, list) and children:
                for child in children:
                    if not isinstance(child, dict):
                        continue
                    name = child.get("geoName") or child.get("name")
                    if not name:
                        continue
                    values = child.get("value", [])
                    if isinstance(values, list):
                        for idx, value in enumerate(values):
                            if idx < len(terms):
                                result["interesse_por_regiao"][terms[idx]][str(name)] = _safe_float(value) or 0
                    else:
                        for term in terms:
                            result["interesse_por_regiao"][term][str(name)] = _safe_float(values) or 0
                continue
            name = entry.get("geoName") or entry.get("name")
            if not name:
                continue
            values = entry.get("value", [])
            if isinstance(values, list):
                for idx, value in enumerate(values):
                    if idx < len(terms):
                        result["interesse_por_regiao"][terms[idx]][str(name)] = _safe_float(value) or 0
            elif values is not None:
                for term in terms:
                    result["interesse_por_regiao"][term][str(name)] = _safe_float(values) or 0

    def _parse_related_payload(self, payload: Any, result: dict, terms: list[str]) -> None:
        data = payload.get("default", payload) if isinstance(payload, dict) else {}
        ranked_lists = data.get("rankedList", []) if isinstance(data, dict) else []
        if not isinstance(ranked_lists, list):
            return
        for term in terms:
            result["queries_relacionadas"].setdefault(term, {"rising": [], "top": []})
        for idx, ranked in enumerate(ranked_lists):
            if not isinstance(ranked, dict):
                continue
            default_bucket = "top" if idx == 0 else "rising"
            keywords = ranked.get("rankedKeyword", [])
            if not isinstance(keywords, list):
                continue
            for kw in keywords:
                if not isinstance(kw, dict):
                    continue
                query = kw.get("query") or kw.get("topic") or kw.get("title")
                if not query:
                    continue
                formatted = str(kw.get("formattedValue") or "").lower()
                bucket = "rising" if ("rising" in formatted or kw.get("isRising")) else default_bucket
                for term in terms:
                    result["queries_relacionadas"][term][bucket].append(str(query))

    def lookup(
        self,
        query: str,
        *,
        period: str = "today 5-Y",
        geo: str = "BR",
        category: int = 0,
        include_related: bool = True,
        include_autocomplete: bool = False,
    ) -> dict:
        terms = [normalize_term(part) for part in query.split(",") if normalize_term(part)]
        if not terms:
            return make_envelope(
                query,
                empty_data([]),
                provenance_url="",
                errors=[make_error("invalid_query", "Termo de busca vazio", "validation")],
            )

        data, errors = self.explore(terms, period=period, geo=geo, category=category)
        if not include_related:
            data["queries_relacionadas"] = {}
        if include_autocomplete and terms:
            data["autocomplete_suggestions"] = self.autocomplete(terms[0])

        provenance_url = (
            f"https://trends.google.com/trends/explore?"
            f"q={urllib.parse.quote(','.join(terms))}"
            f"&geo={geo}&date={decode_period(period).replace(' ', '%20')}"
        )
        return make_envelope(
            query,
            data,
            provenance_url=provenance_url,
            method="api",
            raw_cached=False,
            errors=errors,
            provenance_extra={"geo": geo, "period": decode_period(period)},
        )
