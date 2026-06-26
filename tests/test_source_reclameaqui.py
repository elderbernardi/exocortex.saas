"""Testes unitários e smoke test para excrtx-source-reclameaqui."""

from __future__ import annotations

import json
import os
import sys

import httpx
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.excrtx_source_reclameaqui.collector import BASE_URL, ReclameAquiCollector
from tools.excrtx_source_reclameaqui.schemas import (
    make_envelope,
    now_utc,
    parse_float,
    parse_int,
    parse_percentage,
    slugify_query,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

CLOUDFLARE_HTML = """<!DOCTYPE html><html lang="en-US"><head>
<title>Just a moment...</title>
</head><body>
<div class="main-content"><noscript><div class="h2"><span id="challenge-error-text">Enable JavaScript and cookies to continue</span></div></noscript></div>
<script nonce="abc">window._cf_chl_opt = {cType: 'managed'};</script>
</body></html>"""

NEXT_DATA_HTML = """<!DOCTYPE html><html><head>
<script id="__NEXT_DATA__" type="application/json">{
  "props": {"pageProps": {
    "company": {
      "name": "Girando Sol",
      "score": "7.3",
      "totalComplaints": "142",
      "answered": "138",
      "solutionRate": "87%",
      "categories": [
        {"name": "Propaganda enganosa", "count": "23"},
        {"name": "Qualidade do produto", "count": "18"}
      ]
    },
    "complaints": {
      "list": [
        {"title": "Produto veio com defeito", "created": "2026-05-12", "status": "respondida", "category": "Qualidade do produto"},
        {"title": "Entrega atrasada", "created": "2026-05-10", "status": "não respondida", "category": "Entrega"}
      ]
    }
  }}
}</script>
</head><body><div id="__next"></div></body></html>"""

PLAIN_HTML = """<!DOCTYPE html><html><head><title>Girando Sol - Reclame Aqui</title></head><body>
<h1>Girando Sol</h1>
<div class="score-value">6.8</div>
<div class="complaint-count">95 reclamações</div>
<div class="answered-count">90 respondidas</div>
<div class="resolution-rate">85%</div>
<article class="complaint-card">
  <h2>Produto com defeito</h2>
  <time>10/05/2026</time>
  <span class="status">Respondida</span>
  <span class="tag">Qualidade</span>
</article>
</body></html>"""

NOT_FOUND_HTML = """<!DOCTYPE html><html><head><title>404 - Página não encontrada</title></head>
<body><h1>Empresa não encontrada</h1></body></html>"""


def make_transport(handler):
    return httpx.MockTransport(handler)


# ---------------------------------------------------------------------------
# Helper tests
# ---------------------------------------------------------------------------

class TestSlugify:
    def test_simple_name(self):
        assert slugify_query("Girando Sol") == "girando-sol"

    def test_url_path(self):
        assert slugify_query("/empresa/girando-sol/") == "girando-sol"

    def test_full_url(self):
        assert slugify_query("https://www.reclameaqui.com.br/empresa/girando-sol/") == "girando-sol"

    def test_accents(self):
        assert slugify_query("João & Maria") == "joao-maria"

    def test_empty(self):
        assert slugify_query("") == ""

    def test_slug_passthrough(self):
        assert slugify_query("girando-sol") == "girando-sol"


class TestParseHelpers:
    def test_parse_float_comma(self):
        assert parse_float("7,3") == 7.3

    def test_parse_float_dot(self):
        assert parse_float("7.3") == 7.3

    def test_parse_float_none(self):
        assert parse_float(None) is None

    def test_parse_int_thousands(self):
        assert parse_int("1.234") == 1234

    def test_parse_int_none(self):
        assert parse_int(None) is None

    def test_parse_percentage(self):
        assert parse_percentage("87%") == 0.87

    def test_parse_percentage_fraction(self):
        assert parse_percentage("0.87") == 0.87


class TestEnvelope:
    def test_make_envelope_schema(self):
        envelope = make_envelope("girando-sol", {"empresa": "Girando Sol"}, "https://www.reclameaqui.com.br/empresa/girando-sol/")
        assert envelope["source"] == "reclameaqui"
        assert envelope["query"] == "girando-sol"
        assert "retrieved_at" in envelope
        assert envelope["provenance"]["method"] == "html"
        assert envelope["errors"] == []

    def test_make_envelope_with_errors(self):
        envelope = make_envelope(
            "test",
            None,
            "",
            errors=[{"code": "test", "message": "test error"}],
        )
        assert len(envelope["errors"]) == 1


# ---------------------------------------------------------------------------
# Collector tests
# ---------------------------------------------------------------------------

class TestCollector:
    def test_cloudflare_challenge_detected(self):
        """When RA returns Cloudflare challenge, collector reports structured error."""
        def handler(request: httpx.Request) -> httpx.Response:
            url_str = str(request.url)
            if "girando-sol" in url_str:
                return httpx.Response(403, text=CLOUDFLARE_HTML)
            raise AssertionError(f"URL inesperada: {request.url}")

        collector = ReclameAquiCollector(transport=make_transport(handler))
        result = collector.lookup("Girando Sol")

        assert result["source"] == "reclameaqui"
        assert result["query"] == "Girando Sol"
        assert len(result["errors"]) == 1
        assert result["errors"][0]["code"] == "cloudflare_challenge"
        assert result["errors"][0]["source"] == "cloudflare"
        assert result["data"]["empresa"] is None

    def test_cloudflare_503_detected(self):
        """503 with Cloudflare body is also detected."""
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(503, text=CLOUDFLARE_HTML)

        collector = ReclameAquiCollector(transport=make_transport(handler))
        result = collector.lookup("Girando Sol")

        assert len(result["errors"]) == 1
        assert result["errors"][0]["code"] == "cloudflare_challenge"

    def test_next_data_parsing(self):
        """When HTML contains __NEXT_DATA__, extract company info from it."""
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, text=NEXT_DATA_HTML)

        collector = ReclameAquiCollector(transport=make_transport(handler))
        result = collector.lookup("girando-sol")

        assert result["errors"] == []
        assert result["data"]["empresa"] == "Girando Sol"
        assert result["data"]["nota_geral"] == 7.3
        assert result["data"]["total_reclamacoes"] == 142
        assert result["data"]["respondidas"] == 138
        assert result["data"]["taxa_resolucao"] == 0.87
        assert len(result["data"]["categorias_problema"]) == 2
        assert len(result["data"]["reclamacoes"]) == 2
        assert result["provenance"]["url"].endswith("/girando-sol/")

    def test_plain_html_parsing(self):
        """When HTML has no __NEXT_DATA__, parse from HTML elements."""
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, text=PLAIN_HTML)

        collector = ReclameAquiCollector(transport=make_transport(handler))
        result = collector.lookup("girando-sol")

        assert result["errors"] == []
        assert result["data"]["empresa"] == "Girando Sol"
        assert result["data"]["nota_geral"] == 6.8
        assert result["data"]["slug"] == "girando-sol"
        assert result["data"]["reclamacoes"] is not None

    def test_404_returns_not_found(self):
        """404 returns structured not_found error."""
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(404, text=NOT_FOUND_HTML)

        collector = ReclameAquiCollector(transport=make_transport(handler))
        result = collector.lookup("empresa-inexistente-xyz")

        assert len(result["errors"]) == 1
        assert result["errors"][0]["code"] == "not_found"

    def test_network_timeout(self):
        """Timeout returns structured network error."""
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.TimeoutException("timeout")

        collector = ReclameAquiCollector(transport=make_transport(handler))
        result = collector.lookup("girando-sol")

        assert len(result["errors"]) == 1
        assert result["errors"][0]["code"] == "timeout"

    def test_rate_limit_429(self):
        """429 returns structured rate limit error."""
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(429, text="Rate limited")

        collector = ReclameAquiCollector(transport=make_transport(handler))
        result = collector.lookup("girando-sol")

        assert len(result["errors"]) == 1
        assert result["errors"][0]["code"] == "rate_limited"

    def test_invalid_query_empty_slug(self):
        """Empty query that produces empty slug returns validation error."""
        collector = ReclameAquiCollector()
        result = collector.lookup("!!!")

        assert len(result["errors"]) == 1
        assert result["errors"][0]["code"] == "invalid_query"

    def test_url_input_produces_correct_slug(self):
        """Full URL input is correctly slugified."""
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, text=PLAIN_HTML)

        collector = ReclameAquiCollector(transport=make_transport(handler))
        result = collector.lookup("https://www.reclameaqui.com.br/empresa/girando-sol/")

        assert result["errors"] == []
        assert "girando-sol" in result["provenance"]["url"]

    def test_http_500_error(self):
        """Server error returns structured error."""
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500, text="Internal Server Error")

        collector = ReclameAquiCollector(transport=make_transport(handler))
        result = collector.lookup("girando-sol")

        assert len(result["errors"]) == 1
        assert result["errors"][0]["code"] == "http_error"

    def test_company_with_no_complaints_next_data(self):
        """Company page with zero complaints in NEXT_DATA."""
        empty_next_data = """<html><head>
<script id="__NEXT_DATA__" type="application/json">{
  "props": {"pageProps": {
    "company": {"name": "Empresa Sem Reclamação", "score": "10", "totalComplaints": "0"},
    "complaints": {"list": []}
  }}
}</script></head><body></body></html>"""

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, text=empty_next_data)

        collector = ReclameAquiCollector(transport=make_transport(handler))
        result = collector.lookup("empresa-sem-reclamacao")

        assert result["errors"] == []
        assert result["data"]["empresa"] == "Empresa Sem Reclamação"
        assert result["data"]["total_reclamacoes"] == 0
        assert result["data"]["reclamacoes"] == []


# ---------------------------------------------------------------------------
# Slow / smoke tests (real network)
# ---------------------------------------------------------------------------

@pytest.mark.slow
def test_cli_smoke_real_lookup():
    """Smoke test: real HTTP request to RA. Expects Cloudflare block."""
    import subprocess

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.excrtx_source_reclameaqui.cli",
            "Girando Sol",
            "--output",
            "json",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=os.path.join(os.path.dirname(__file__), ".."),
    )

    # Even blocked by Cloudflare, output should be valid JSON
    payload = json.loads(result.stdout)
    assert payload["source"] == "reclameaqui"
    assert payload["query"] == "Girando Sol"
    assert "retrieved_at" in payload
    assert "data" in payload
    assert "errors" in payload

    # In the current runtime, we expect Cloudflare block
    if payload["errors"]:
        assert payload["errors"][0]["code"] == "cloudflare_challenge", (
            f"Esperado cloudflare_challenge, recebido: {payload['errors'][0]['code']}"
        )
