"""Testes unitários e smoke test para excrtx-source-google-trends."""

from __future__ import annotations

import json
import os
import sys

import httpx
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.excrtx_source_google_trends.collector import GoogleTrendsCollector
from tools.excrtx_source_google_trends.schemas import (
    decode_period,
    empty_data,
    make_envelope,
    make_error,
    normalize_term,
    today_utc,
    ts_to_partial,
)


class TestHelpers:
    def test_normalize_term_strips(self):
        assert normalize_term("  Girando   Sol  ") == "Girando Sol"

    def test_normalize_term_empty(self):
        assert normalize_term("") == ""

    def test_today_utc_format(self):
        ts = today_utc()
        assert "T" in ts
        assert ts.endswith("Z")

    def test_ts_to_partial(self):
        assert ts_to_partial("2025-06-15") == "2025-06"
        assert ts_to_partial("2025-06") == "2025-06"

    def test_decode_period_aliases(self):
        assert decode_period("7d") == "today 7-d"
        assert decode_period("1m") == "today 1-m"
        assert decode_period("5y") == "today 5-y"
        assert decode_period(None) == "today 5-Y"

    def test_decode_period_range(self):
        assert decode_period("2025-01-01 2026-06-25") == "2025-01-01 2026-06-25"

    def test_empty_data(self):
        data = empty_data(["term1"])
        assert data["termos"] == ["term1"]
        assert data["serie_temporal"] == {}
        assert data["interesse_por_regiao"] == {}
        assert data["queries_relacionadas"] == {}

    def test_make_error(self):
        err = make_error("test_code", "test message", "test_source")
        assert err["code"] == "test_code"
        assert err["message"] == "test message"
        assert err["source"] == "test_source"

    def test_make_error_no_source(self):
        err = make_error("code", "msg")
        assert "source" not in err

    def test_make_envelope_schema(self):
        envelope = make_envelope("test", {"termos": ["test"]}, "https://example.com")
        assert envelope["source"] == "google_trends"
        assert envelope["query"] == "test"
        assert "retrieved_at" in envelope
        assert envelope["provenance"]["method"] == "api"
        assert envelope["errors"] == []

    def test_make_envelope_with_errors(self):
        envelope = make_envelope("q", None, "", errors=[make_error("err", "fail")])
        assert len(envelope["errors"]) == 1
        assert envelope["data"]["termos"] == []


def make_transport(handler):
    return httpx.MockTransport(handler)


class TestCollector:
    def test_lookup_basic_explore(self):
        def handler(request: httpx.Request) -> httpx.Response:
            url = str(request.url)
            if "explore" in url:
                return httpx.Response(200, json={
                    "widgets": [
                        {
                            "id": "TIMESERIES",
                            "data": {
                                "timelineData": [
                                    {
                                        "formattedTime": "Jun 2021",
                                        "value": [42],
                                    },
                                    {
                                        "formattedTime": "Jul 2021",
                                        "value": [55],
                                    },
                                ]
                            }
                        }
                    ]
                })
            raise AssertionError(f"URL inesperada: {request.url}")

        collector = GoogleTrendsCollector(transport=make_transport(handler))
        result = collector.lookup("Girando Sol", period="5y", geo="BR")

        assert result["errors"] == []
        assert result["source"] == "google_trends"
        assert result["query"] == "Girando Sol"
        assert "Girando Sol" in result["data"]["termos"]
        assert "Girando Sol" in result["data"]["serie_temporal"]
        assert len(result["data"]["serie_temporal"]["Girando Sol"]) == 2
        assert result["data"]["serie_temporal"]["Girando Sol"][0]["value"] == 42
        assert result["provenance"]["url"].startswith("https://trends.google.com/")

    def test_lookup_multi_term(self):
        def handler(request: httpx.Request) -> httpx.Response:
            url = str(request.url)
            if "explore" in url:
                return httpx.Response(200, json={
                    "widgets": [
                        {
                            "id": "TIMESERIES",
                            "data": {
                                "timelineData": [
                                    {
                                        "formattedTime": "Jun 2021",
                                        "value": [42, 88],
                                    },
                                ]
                            }
                        }
                    ]
                })
            raise AssertionError(f"URL inesperada: {request.url}")

        collector = GoogleTrendsCollector(transport=make_transport(handler))
        result = collector.lookup("Girando Sol, Omo", period="5y", geo="BR")

        assert result["errors"] == []
        assert len(result["data"]["termos"]) == 2
        assert "Girando Sol" in result["data"]["serie_temporal"]
        assert "Omo" in result["data"]["serie_temporal"]

    def test_lookup_with_geo(self):
        def handler(request: httpx.Request) -> httpx.Response:
            url = str(request.url)
            if "explore" in url:
                return httpx.Response(200, json={
                    "widgets": [
                        {
                            "id": "GEO_MAP",
                            "data": {
                                "geoMapData": [
                                    {
                                        "children": [
                                            {"name": "Rio Grande do Sul", "value": 100},
                                            {"name": "Santa Catarina", "value": 72},
                                        ]
                                    }
                                ]
                            }
                        }
                    ]
                })
            raise AssertionError(f"URL inesperada: {request.url}")

        collector = GoogleTrendsCollector(transport=make_transport(handler))
        result = collector.lookup("Girando Sol", period="5y", geo="BR")

        assert result["errors"] == []
        geo_data = result["data"]["interesse_por_regiao"].get("Girando Sol", {})
        assert geo_data.get("Rio Grande do Sul") == 100
        assert geo_data.get("Santa Catarina") == 72

    def test_lookup_with_related_queries(self):
        def handler(request: httpx.Request) -> httpx.Response:
            url = str(request.url)
            if "explore" in url:
                return httpx.Response(200, json={
                    "widgets": [
                        {
                            "id": "RELATED_QUERIES",
                            "data": {
                                "rankedList": [
                                    {
                                        "rankedKeyword": [
                                            {"query": "girando sol coco", "formattedValue": "rising", "value": 500},
                                            {"query": "girando sol produtos", "formattedValue": "200", "value": 200},
                                        ]
                                    }
                                ]
                            }
                        }
                    ]
                })
            raise AssertionError(f"URL inesperada: {request.url}")

        collector = GoogleTrendsCollector(transport=make_transport(handler))
        result = collector.lookup("Girando Sol", period="5y", geo="BR")

        assert result["errors"] == []
        qq = result["data"]["queries_relacionadas"].get("Girando Sol", {})
        assert "girando sol coco" in qq.get("rising", [])
        assert "girando sol produtos" in qq.get("top", [])

    def test_lookup_empty_query(self):
        collector = GoogleTrendsCollector(transport=make_transport(lambda r: httpx.Response(200, json={})))
        result = collector.lookup("   ")

        assert len(result["errors"]) == 1
        assert result["errors"][0]["code"] == "invalid_query"

    def test_lookup_api_failure(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(429, json={"error": "rate limited"})

        collector = GoogleTrendsCollector(transport=make_transport(handler))
        result = collector.lookup("Girando Sol", period="5y", geo="BR")

        assert len(result["errors"]) >= 1
        assert any(e["code"] == "rate_limited" for e in result["errors"])

    def test_lookup_default_format(self):
        """Test parsing with 'default' top-level key format."""
        def handler(request: httpx.Request) -> httpx.Response:
            url = str(request.url)
            if "explore" in url:
                return httpx.Response(200, json={
                    "default": {
                        "timelineData": [
                            {"formattedTime": "2025-06-15", "value": [30]},
                        ],
                        "geoMapData": [
                            {"children": [{"name": "São Paulo", "value": 50}]}
                        ],
                    }
                })
            raise AssertionError(f"URL inesperada: {request.url}")

        collector = GoogleTrendsCollector(transport=make_transport(handler))
        result = collector.lookup("Test", period="5y", geo="BR")

        assert result["errors"] == []
        assert "Test" in result["data"]["serie_temporal"]
        assert result["data"]["serie_temporal"]["Test"][0]["date"] == "2025-06"

    def test_autocomplete(self):
        def handler(request: httpx.Request) -> httpx.Response:
            url = str(request.url)
            if "autocomplete" in url:
                return httpx.Response(200, json=["Girando Sol", ["girando sol produtos", "girando sol coco"]])
            raise AssertionError(f"URL inesperada: {request.url}")

        collector = GoogleTrendsCollector(transport=make_transport(handler))
        suggestions = collector.autocomplete("Girando Sol")

        assert "girando sol produtos" in suggestions

    def test_autocomplete_empty(self):
        collector = GoogleTrendsCollector(transport=make_transport(lambda r: httpx.Response(200, json=[])))
        assert collector.autocomplete("") == []

    def test_lookup_with_autocomplete(self):
        calls = {"explore": 0, "autocomplete": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            url = str(request.url)
            if "explore" in url:
                calls["explore"] += 1
                return httpx.Response(200, json={"widgets": []})
            if "autocomplete" in url:
                calls["autocomplete"] += 1
                return httpx.Response(200, json=["Girando Sol", ["girando sol shampoo"]])
            raise AssertionError(f"URL inesperada: {request.url}")

        collector = GoogleTrendsCollector(transport=make_transport(handler))
        result = collector.lookup("Girando Sol", include_autocomplete=True)

        assert calls["autocomplete"] == 1
        assert "girando sol shampoo" in result["data"].get("autocomplete_suggestions", [])


class TestCLI:
    def test_cli_help(self):
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "tools.excrtx_source_google_trends.cli", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.path.join(os.path.dirname(__file__), ".."),
        )
        assert result.returncode == 0
        assert "query" in result.stdout.lower() or "termo" in result.stdout.lower()

    def test_cli_json_output(self):
        import subprocess
        result = subprocess.run(
            [
                sys.executable, "-m", "tools.excrtx_source_google_trends.cli",
                "TestTerm", "--output", "json", "--period", "5y",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.path.join(os.path.dirname(__file__), ".."),
            env={**os.environ, "PYTHONPATH": os.path.join(os.path.dirname(__file__), "..")},
        )
        assert result.returncode in (0, 1)
        payload = json.loads(result.stdout)
        assert payload["source"] == "google_trends"
        assert payload["query"] == "TestTerm"
        if result.returncode == 1:
            assert any(err["code"] == "rate_limited" for err in payload["errors"])


@pytest.mark.slow
def test_cli_smoke_real_lookup():
    """Smoke real: consulta Google Trends público; aceita rate limit verificável."""
    import subprocess

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.excrtx_source_google_trends.cli",
            "Girando Sol",
            "--output",
            "json",
            "--period",
            "5y",
            "--geo",
            "BR",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=os.path.join(os.path.dirname(__file__), ".."),
    )

    assert result.returncode in (0, 1), result.stderr or result.stdout
    payload = json.loads(result.stdout)
    assert payload["source"] == "google_trends"
    assert payload["query"] == "Girando Sol"
    assert payload["data"]["termos"] == ["Girando Sol"]
    if result.returncode == 0:
        assert payload["errors"] == []
    else:
        assert any(err["code"] == "rate_limited" for err in payload["errors"])
