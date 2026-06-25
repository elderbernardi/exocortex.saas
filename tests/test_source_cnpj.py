"""Testes unitários e smoke test para excrtx-source-cnpj."""

from __future__ import annotations

import json
import os
import sys
import tempfile

import httpx
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.excrtx_source_cnpj.collector import BRASILAPI_URL, RECEITAWS_URL, CNPJCollector, Cache
from tools.excrtx_source_cnpj.schemas import make_envelope, normalize_cnpj, parse_br_date, parse_capital_social


class TestHelpers:
    def test_normalize_cnpj_accepts_masked(self):
        assert normalize_cnpj("12.345.678/0001-90") == "12345678000190"

    def test_normalize_cnpj_rejects_invalid_length(self):
        with pytest.raises(ValueError):
            normalize_cnpj("123")

    def test_parse_br_date(self):
        assert parse_br_date("03/11/2021") == "2021-11-03"
        assert parse_br_date("2021-11-03") == "2021-11-03"

    def test_parse_capital_social(self):
        assert parse_capital_social("1.234,56") == 1234.56
        assert parse_capital_social("1234.56") == 1234.56

    def test_make_envelope_schema(self):
        envelope = make_envelope("12345678000190", {"cnpj": "12345678000190"}, "https://example.com")
        assert envelope["source"] == "cnpj"
        assert envelope["query"] == "12345678000190"
        assert "retrieved_at" in envelope
        assert envelope["provenance"]["method"] == "api"


class TestCache:
    def test_cache_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = Cache(cache_dir=tmpdir, ttl_seconds=60)
            payload = {"ok": True}
            cache.set("12345678000190", payload)
            assert cache.get("12345678000190") == payload


def make_transport(handler):
    return httpx.MockTransport(handler)


class TestCollector:
    def test_lookup_uses_brasilapi_primary(self):
        def handler(request: httpx.Request) -> httpx.Response:
            if str(request.url) == BRASILAPI_URL.format(cnpj="12345678000190"):
                return httpx.Response(200, json={
                    "cnpj": "12345678000190",
                    "razao_social": "Empresa Teste SA",
                    "nome_fantasia": "Empresa Teste",
                    "data_inicio_atividade": "2021-11-03",
                    "capital_social": "12345.67",
                    "descricao_situacao_cadastral": "ATIVA",
                    "cnae_fiscal": 2062200,
                    "cnae_fiscal_descricao": "Fabricação de sabões e detergentes sintéticos",
                    "cnaes_secundarios": [{"codigo": 4649408, "descricao": "Comércio atacadista de produtos de higiene"}],
                    "qsa": [{"nome_socio": "Maria da Silva", "qualificacao_socio": "Sócio-Administrador"}],
                })
            raise AssertionError(f"URL inesperada: {request.url}")

        collector = CNPJCollector(transport=make_transport(handler), use_cache=False)
        result = collector.lookup("12.345.678/0001-90")

        assert result["errors"] == []
        assert result["source"] == "cnpj"
        assert result["data"]["cnpj"] == "12345678000190"
        assert result["data"]["razao_social"] == "Empresa Teste SA"
        assert result["data"]["capital_social"] == 12345.67
        assert len(result["data"]["cnaes"]) == 2
        assert result["provenance"]["url"].startswith("https://brasilapi.com.br/")

    def test_lookup_falls_back_to_receitaws(self):
        def handler(request: httpx.Request) -> httpx.Response:
            url = str(request.url)
            if url == BRASILAPI_URL.format(cnpj="12345678000190"):
                return httpx.Response(503, json={"message": "temporarily unavailable"})
            if url == RECEITAWS_URL.format(cnpj="12345678000190"):
                return httpx.Response(200, json={
                    "status": "OK",
                    "nome": "Empresa Fallback Ltda",
                    "fantasia": "Fallback",
                    "abertura": "03/11/2021",
                    "capital_social": "9.999,90",
                    "situacao": "ATIVA",
                    "atividade_principal": [{"code": "20.62-2-00", "text": "Fabricação de sabões"}],
                    "atividades_secundarias": [],
                    "qsa": [{"nome": "João Souza", "qual": "Administrador"}],
                })
            raise AssertionError(f"URL inesperada: {request.url}")

        collector = CNPJCollector(transport=make_transport(handler), use_cache=False)
        result = collector.lookup("12345678000190")

        assert result["errors"] == []
        assert result["data"]["razao_social"] == "Empresa Fallback Ltda"
        assert result["data"]["capital_social"] == 9999.90
        assert result["provenance"]["url"].startswith("https://www.receitaws.com.br/")

    def test_lookup_returns_structured_error_when_all_sources_fail(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(404, json={"message": "not found"})

        collector = CNPJCollector(transport=make_transport(handler), use_cache=False)
        result = collector.lookup("12345678000190")

        assert result["data"]["cnpj"] == "12345678000190"
        assert len(result["errors"]) == 2
        assert all("code" in error for error in result["errors"])

    def test_lookup_uses_cache_on_second_call(self):
        calls = {"count": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            calls["count"] += 1
            return httpx.Response(200, json={
                "cnpj": "12345678000190",
                "razao_social": "Cache SA",
                "nome_fantasia": None,
                "data_inicio_atividade": "2021-11-03",
                "capital_social": "123.45",
                "descricao_situacao_cadastral": "ATIVA",
                "cnae_fiscal": 2062200,
                "cnae_fiscal_descricao": "Fabricação",
                "cnaes_secundarios": [],
                "qsa": [],
            })

        with tempfile.TemporaryDirectory() as tmpdir:
            collector = CNPJCollector(transport=make_transport(handler), cache_dir=tmpdir, use_cache=True)
            first = collector.lookup("12345678000190")
            second = collector.lookup("12345678000190")

        assert first["errors"] == []
        assert second["errors"] == []
        assert second["provenance"]["raw_cached"] is True
        assert calls["count"] == 1


@pytest.mark.slow
def test_cli_smoke_real_lookup():
    import subprocess

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.excrtx_source_cnpj.cli",
            "33000167000101",
            "--output",
            "json",
            "--no-cache",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=os.path.join(os.path.dirname(__file__), ".."),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(result.stdout)
    assert payload["source"] == "cnpj"
    assert payload["query"] == "33000167000101"
    assert payload["data"]["cnpj"] == "33000167000101"
    assert payload["errors"] == []
