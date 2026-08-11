"""Tests for exact noticias_publicas lookup helpers."""
from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LOOKUP_SCRIPT = REPO_ROOT / "skills" / "excrtx-news-sales-ai" / "scripts" / "lookup_noticias_exact.py"
MATCH_SCRIPT = REPO_ROOT / "skills" / "excrtx-news-sales-ai" / "scripts" / "signal_match_prepare.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeLookupClient:
    def __init__(self):
        self.auth_mode = type("AuthMode", (), {"kind": "password"})()
        self.calls: list[tuple[str, dict[str, str]]] = []

    def fetch_rows(self, table: str, filters: dict[str, str] | None = None):
        filters = dict(filters or {})
        self.calls.append((table, filters))
        assert table == "noticias_publicas"
        return [
            {
                "id": "row-active",
                "url": "https://example.com/active",
                "cliente_id": "client-1",
                "ativo": True,
                "escopo": "micro",
                "publicado_em": "2026-08-10",
                "valido_ate": "2026-09-24",
                "titulo": "Ativa",
            },
            {
                "id": "row-retired",
                "url": "https://example.com/retired",
                "cliente_id": None,
                "ativo": False,
                "escopo": "macro",
                "publicado_em": "2026-08-01",
                "valido_ate": "2026-08-09",
                "titulo": "Retirada",
            },
            {
                "id": "row-wrong-client",
                "url": "https://example.com/active",
                "cliente_id": "client-9",
                "ativo": True,
                "escopo": "micro",
                "publicado_em": "2026-08-10",
                "valido_ate": "2026-09-24",
                "titulo": "Outra carteira",
            },
        ]


def test_lookup_rows_for_candidates_filters_exact_url_and_cliente_pair():
    lookup = load_module(LOOKUP_SCRIPT, "lookup_noticias_exact")
    client = FakeLookupClient()
    rows = lookup.lookup_rows_for_candidates(
        client,
        [
            {"url_normalized": "https://example.com/active", "cliente_id": "client-1"},
            {"url_normalized": "https://example.com/retired", "cliente_id": None},
        ],
    )

    assert [row["id"] for row in rows] == ["row-active", "row-retired"]
    assert client.calls[0][0] == "noticias_publicas"
    assert client.calls[0][1]["url"].startswith("in.(")


def test_rows_payload_wraps_rows_with_schema():
    lookup = load_module(LOOKUP_SCRIPT, "lookup_noticias_exact_payload")
    payload = lookup.rows_payload([{"id": "row-1", "url": "https://example.com/x", "cliente_id": None, "ativo": True}], auth_mode="password")
    assert payload["schema"] == "exocortex/news-lookup-exact/v1"
    assert payload["auth_mode"] == "password"
    assert payload["row_count"] == 1


def test_signal_match_resolve_existing_rows_uses_live_lookup(monkeypatch, tmp_path):
    match = load_module(MATCH_SCRIPT, "signal_match_prepare_lookup")

    class FakeRestClient:
        def __init__(self, env, page_size=500):
            self.auth_mode = type("AuthMode", (), {"kind": "password"})()

    roster_module = types.ModuleType("roster_live_export")
    roster_module.SupabaseRestClient = FakeRestClient
    roster_module.merged_env = lambda env_file: {"SUPABASE_URL": "https://db.test", "SUPABASE_ANON_KEY": "anon", "SUPABASE_USER_EMAIL": "ops@example.com", "SUPABASE_USER_PASSWORD": "secret"}
    monkeypatch.setitem(sys.modules, "roster_live_export", roster_module)
    monkeypatch.setattr(match, "lookup_rows_for_candidates", lambda client, candidates, chunk_size=75: [{"id": "row-1", "url": "https://example.com/active", "cliente_id": "client-1", "ativo": True}])

    rows, source = match.resolve_existing_rows(
        existing_path=None,
        lookup_env_file="/tmp/fake.env",
        lookup_output=str(tmp_path / "lookup.json"),
        publish_candidates=[{"url_normalized": "https://example.com/active", "cliente_id": "client-1"}],
        lookup_page_size=500,
        lookup_chunk_size=75,
    )

    assert source == "live:password"
    assert rows[0]["id"] == "row-1"
    written = json.loads((tmp_path / "lookup.json").read_text(encoding="utf-8"))
    assert written["row_count"] == 1
    assert written["rows"][0]["id"] == "row-1"
