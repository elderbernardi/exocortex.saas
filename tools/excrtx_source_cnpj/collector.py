"""Coletor de dados cadastrais de CNPJ via APIs públicas."""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from .schemas import (
    empty_data,
    make_envelope,
    make_error,
    normalize_cnpj,
    now_utc,
    parse_br_date,
    parse_capital_social,
)

BRASILAPI_URL = "https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
RECEITAWS_URL = "https://www.receitaws.com.br/v1/cnpj/{cnpj}"
USER_AGENT = "exocortex-cnpj-collector/1.0"


@dataclass(frozen=True)
class Endpoint:
    name: str
    url_template: str
    rate_limit_seconds: float = 1.0


ENDPOINTS = [
    Endpoint(name="brasilapi", url_template=BRASILAPI_URL, rate_limit_seconds=0.5),
    Endpoint(name="receitaws", url_template=RECEITAWS_URL, rate_limit_seconds=2.0),
]


class Cache:
    """Cache simples em disco para consultas de CNPJ."""

    def __init__(self, cache_dir: str = "/tmp/excrtx-source-cnpj-cache", ttl_seconds: int = 86400):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds

    def _key(self, cnpj: str) -> str:
        return hashlib.sha256(cnpj.encode()).hexdigest()[:24]

    def get(self, cnpj: str) -> dict | None:
        path = self.cache_dir / f"{self._key(cnpj)}.json"
        if not path.exists():
            return None
        age = time.time() - path.stat().st_mtime
        if age > self.ttl_seconds:
            path.unlink(missing_ok=True)
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def set(self, cnpj: str, payload: dict) -> None:
        path = self.cache_dir / f"{self._key(cnpj)}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class CNPJCollector:
    def __init__(
        self,
        *,
        cache_dir: str = "/tmp/excrtx-source-cnpj-cache",
        cache_ttl_seconds: int = 86400,
        timeout_seconds: float = 20.0,
        transport: httpx.BaseTransport | None = None,
        use_cache: bool = True,
    ):
        self.cache = Cache(cache_dir=cache_dir, ttl_seconds=cache_ttl_seconds)
        self.timeout_seconds = timeout_seconds
        self.transport = transport
        self.use_cache = use_cache
        self._last_request_at: dict[str, float] = {}

    def lookup(self, query: str) -> dict:
        try:
            cnpj = normalize_cnpj(query)
        except ValueError as exc:
            return make_envelope(
                re.sub(r"\D", "", query or ""),
                empty_data(None),
                provenance_url="",
                errors=[make_error("invalid_cnpj", str(exc), "validation")],
            )

        if self.use_cache:
            cached = self.cache.get(cnpj)
            if cached:
                cached["provenance"]["raw_cached"] = True
                return cached

        errors: list[dict] = []
        with httpx.Client(
            timeout=self.timeout_seconds,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            transport=self.transport,
            follow_redirects=True,
        ) as client:
            for endpoint in ENDPOINTS:
                url = endpoint.url_template.format(cnpj=cnpj)
                payload, error = self._request_json(client, endpoint, url)
                if error:
                    errors.append(error)
                    continue

                if endpoint.name == "brasilapi":
                    assert payload is not None
                    data = self._parse_brasilapi(payload, cnpj)
                else:
                    assert payload is not None
                    data = self._parse_receitaws(payload, cnpj)

                envelope = make_envelope(
                    cnpj,
                    data,
                    provenance_url=url,
                    method="api",
                    raw_cached=False,
                    errors=[],
                )
                if self.use_cache:
                    self.cache.set(cnpj, envelope)
                return envelope

        return make_envelope(
            cnpj,
            empty_data(cnpj),
            provenance_url="",
            method="api",
            raw_cached=False,
            errors=errors or [make_error("lookup_failed", "Nenhuma fonte respondeu com sucesso", "collector")],
        )

    def _request_json(self, client: httpx.Client, endpoint: Endpoint, url: str) -> tuple[dict[str, Any] | None, dict | None]:
        self._respect_rate_limit(endpoint.name, endpoint.rate_limit_seconds)
        try:
            response = client.get(url)
        except httpx.TimeoutException:
            return None, make_error("timeout", f"Timeout consultando {endpoint.name}", endpoint.name)
        except httpx.HTTPError as exc:
            return None, make_error("network_error", str(exc), endpoint.name)

        if response.status_code == 404:
            return None, make_error("not_found", "CNPJ não encontrado", endpoint.name)
        if response.status_code == 429:
            return None, make_error("rate_limited", f"Rate limit em {endpoint.name}", endpoint.name)
        if response.status_code >= 400:
            return None, make_error(
                "http_error",
                f"HTTP {response.status_code} em {endpoint.name}",
                endpoint.name,
            )

        try:
            payload = response.json()
        except ValueError:
            return None, make_error("invalid_json", f"Resposta inválida em {endpoint.name}", endpoint.name)

        api_error = self._detect_api_error(endpoint.name, payload)
        if api_error:
            return None, api_error
        return payload, None

    def _respect_rate_limit(self, name: str, seconds: float) -> None:
        if seconds <= 0:
            return
        last = self._last_request_at.get(name)
        now = time.time()
        if last is not None:
            delta = now - last
            if delta < seconds:
                time.sleep(seconds - delta)
        self._last_request_at[name] = time.time()

    @staticmethod
    def _detect_api_error(endpoint_name: str, payload: dict[str, Any]) -> dict | None:
        if not isinstance(payload, dict):
            return make_error("invalid_payload", f"Payload inesperado em {endpoint_name}", endpoint_name)

        if endpoint_name == "brasilapi" and payload.get("message"):
            return make_error("api_error", str(payload["message"]), endpoint_name)

        if endpoint_name == "receitaws":
            status = str(payload.get("status") or "").upper()
            if status == "ERROR":
                return make_error("api_error", str(payload.get("message") or "Erro desconhecido"), endpoint_name)

        return None

    @staticmethod
    def _parse_brasilapi(payload: dict[str, Any], cnpj: str) -> dict:
        cnaes = []
        if payload.get("cnae_fiscal") or payload.get("cnae_fiscal_descricao"):
            cnaes.append(
                {
                    "codigo": str(payload.get("cnae_fiscal") or ""),
                    "descricao": payload.get("cnae_fiscal_descricao") or "",
                }
            )
        for item in payload.get("cnaes_secundarios") or []:
            cnaes.append(
                {
                    "codigo": str(item.get("codigo") or ""),
                    "descricao": item.get("descricao") or "",
                }
            )

        socios = []
        for item in payload.get("qsa") or []:
            socios.append(
                {
                    "nome": item.get("nome_socio") or item.get("nome") or "",
                    "qualificacao": item.get("qualificacao_socio") or item.get("qual") or "",
                }
            )

        return {
            "cnpj": cnpj,
            "razao_social": payload.get("razao_social") or payload.get("nome") or None,
            "nome_fantasia": payload.get("nome_fantasia") or None,
            "data_abertura": parse_br_date(payload.get("data_inicio_atividade") or payload.get("inicio_atividade")),
            "capital_social": parse_capital_social(payload.get("capital_social")),
            "situacao_cadastral": payload.get("descricao_situacao_cadastral") or payload.get("situacao_cadastral") or None,
            "cnaes": cnaes,
            "socios": socios,
            "filiais": [],
        }

    @staticmethod
    def _parse_receitaws(payload: dict[str, Any], cnpj: str) -> dict:
        cnaes = []
        for item in payload.get("atividade_principal") or []:
            cnaes.append(
                {
                    "codigo": str(item.get("code") or item.get("codigo") or ""),
                    "descricao": item.get("text") or item.get("descricao") or "",
                }
            )
        for item in payload.get("atividades_secundarias") or []:
            cnaes.append(
                {
                    "codigo": str(item.get("code") or item.get("codigo") or ""),
                    "descricao": item.get("text") or item.get("descricao") or "",
                }
            )

        socios = []
        for item in payload.get("qsa") or []:
            socios.append(
                {
                    "nome": item.get("nome") or "",
                    "qualificacao": item.get("qual") or item.get("qualificacao") or "",
                }
            )

        return {
            "cnpj": cnpj,
            "razao_social": payload.get("nome") or None,
            "nome_fantasia": payload.get("fantasia") or None,
            "data_abertura": parse_br_date(payload.get("abertura")),
            "capital_social": parse_capital_social(payload.get("capital_social")),
            "situacao_cadastral": payload.get("situacao") or None,
            "cnaes": cnaes,
            "socios": socios,
            "filiais": [],
        }
