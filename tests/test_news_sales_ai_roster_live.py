"""Tests for live roster export helpers in excrtx-news-sales-ai."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "skills" / "excrtx-news-sales-ai" / "scripts" / "roster_live_export.py"


def load_module():
    spec = importlib.util.spec_from_file_location("roster_live_export", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeClient:
    def __init__(self):
        self.auth_mode = type("AuthMode", (), {"kind": "password"})()
        self.calls: list[tuple[str, dict[str, str]]] = []

    def fetch_rows(self, table: str, filters: dict[str, str] | None = None):
        filters = dict(filters or {})
        self.calls.append((table, filters))
        if table == "vendedores":
            return [
                {
                    "id": "seller-1",
                    "nome": "Alice",
                    "role": "vendedor",
                    "ativo": True,
                    "erp_ref_codes": ["10"],
                },
                {
                    "id": "seller-2",
                    "nome": "<SEM VENDEDOR>",
                    "role": "vendedor",
                    "ativo": True,
                    "erp_ref_codes": ["20"],
                },
                {
                    "id": "seller-3",
                    "nome": "Bob",
                    "role": "vendedor",
                    "ativo": True,
                    "erp_ref_codes": [],
                },
            ]
        if table == "cliente_acesso":
            assert filters["vendedor_id"] == "in.(seller-1)"
            return [
                {"vendedor_id": "seller-1", "cliente_id": "client-1", "tipo": "titular"},
                {"vendedor_id": "seller-1", "cliente_id": "client-2", "tipo": "compartilhado"},
            ]
        if table == "clientes":
            assert filters["status"] == "eq.ativo"
            assert filters["tabela_atual"] == "not.is.null"
            assert filters["rfm_label"] == "not.is.null"
            return [
                {
                    "id": "client-1",
                    "nome": "Rede Um Ltda",
                    "nome_fantasia": "Rede Um",
                    "cnpj": "123",
                    "cidade": "Porto Alegre",
                    "uf": "RS",
                    "status": "ativo",
                    "tabela_atual": "191 - REDE UM",
                    "rfm_label": "A",
                },
            ]
        raise AssertionError(f"unexpected table {table}")


def test_resolve_auth_mode_prefers_password_when_email_and_password_are_present():
    module = load_module()
    auth = module.resolve_auth_mode(
        {
            "SUPABASE_URL": "https://db.test",
            "SUPABASE_USER_EMAIL": "ops@example.com",
            "SUPABASE_USER_PASSWORD": "secret",
            "SUPABASE_ANON_KEY": "anon",
        }
    )
    assert auth.kind == "password"
    assert auth.email == "ops@example.com"


def test_collect_live_inputs_filters_to_eligible_seller_and_matrix_clients():
    module = load_module()
    fake = FakeClient()
    payloads = module.collect_live_inputs(fake)

    assert payloads["vendedores"]["total_count"] == 1
    assert payloads["vendedores"]["data"][0]["id"] == "seller-1"
    assert payloads["clientes"]["total_count"] == 1
    assert payloads["clientes"]["data"][0]["id"] == "client-1"
    assert payloads["acessos"]["total_count"] == 1
    assert payloads["acessos"]["data"][0]["cliente_id"] == "client-1"
    assert [table for table, _ in fake.calls] == ["vendedores", "cliente_acesso", "clientes"]


def test_write_raw_exports_and_freeze_from_payloads(tmp_path):
    module = load_module()
    payloads = {
        "vendedores": {
            "schema": "exocortex/micro-news-roster-input/v1",
            "kind": "vendedores",
            "generated_at": "2026-08-11T00:00:00Z",
            "auth_mode": "password",
            "total_count": 1,
            "data": [
                {
                    "id": "seller-1",
                    "nome": "Alice",
                    "email": "alice@example.com",
                    "role": "vendedor",
                    "ativo": True,
                    "erp_ref_code": "10",
                    "erp_ref_codes": ["10"],
                }
            ],
        },
        "clientes": {
            "schema": "exocortex/micro-news-roster-input/v1",
            "kind": "clientes",
            "generated_at": "2026-08-11T00:00:00Z",
            "auth_mode": "password",
            "total_count": 1,
            "data": [
                {
                    "id": "client-1",
                    "nome": "Rede Um Ltda",
                    "nome_fantasia": "Rede Um",
                    "cnpj": "12345678000190",
                    "cidade": "Porto Alegre",
                    "uf": "RS",
                    "status": "ativo",
                    "tabela_atual": "191 - REDE UM",
                    "rfm_label": "A",
                    "matriz_id": None,
                    "erp_ref_code": "500",
                }
            ],
        },
        "acessos": {
            "schema": "exocortex/micro-news-roster-input/v1",
            "kind": "cliente_acesso",
            "generated_at": "2026-08-11T00:00:00Z",
            "auth_mode": "password",
            "total_count": 1,
            "data": [{"vendedor_id": "seller-1", "cliente_id": "client-1", "tipo": "titular"}],
        },
    }

    raw_paths = module.write_raw_exports(payloads, str(tmp_path / "raw"))
    assert set(raw_paths) == {"vendedores", "clientes", "acessos"}
    written = json.loads(Path(raw_paths["vendedores"]).read_text(encoding="utf-8"))
    assert written["data"][0]["id"] == "seller-1"

    summary = module.freeze_from_payloads(payloads, str(tmp_path / "freeze"))
    assert summary["seller_count"] == 1
    assert summary["client_count_total"] == 1
    manifest = json.loads((tmp_path / "freeze" / "sellers" / "seller-1.json").read_text(encoding="utf-8"))
    assert manifest["clients"][0]["cliente_id"] == "client-1"
