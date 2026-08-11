"""Tests for deterministic micro-news signal matching."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "skills" / "excrtx-news-sales-ai" / "scripts" / "signal_match_prepare.py"


def load_module():
    spec = importlib.util.spec_from_file_location("signal_match_prepare", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_manifest_fixture(root: Path) -> Path:
    manifests = root / "manifests"
    sellers = manifests / "sellers"
    sellers.mkdir(parents=True, exist_ok=True)
    (manifests / "index.json").write_text(
        json.dumps(
            {
                "schema": "exocortex/micro-news-roster/v1",
                "generated_at": "2026-08-11T00:00:00Z",
                "seller_count": 1,
                "client_count_total": 1,
                "sellers": [
                    {
                        "seller_id": "seller-1",
                        "seller_name": "Alice",
                        "seller_email": "alice@example.com",
                        "client_count": 1,
                        "json_path": "sellers/seller-1.json",
                        "csv_path": "sellers/seller-1.csv",
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (sellers / "seller-1.json").write_text(
        json.dumps(
            {
                "schema": "exocortex/micro-news-roster/v1",
                "generated_at": "2026-08-11T00:00:00Z",
                "seller": {"seller_id": "seller-1", "seller_name": "Alice", "seller_email": "alice@example.com"},
                "client_count": 1,
                "clients": [
                    {
                        "cliente_id": "client-1",
                        "nome": "Rede Um Ltda",
                        "nome_fantasia": "Rede Um",
                        "cnpj": "12345678000190",
                        "cidade": "Porto Alegre",
                        "uf": "RS",
                        "erp_ref_code": "500",
                        "tabela_atual": "191 - REDE UM",
                        "rfm_label": "A",
                        "matriz_id": None,
                        "access_types": ["titular"],
                        "aliases": ["rede um ltda", "rede um", "12345678000190", "porto alegre rs"],
                        "brand_aliases": [],
                    }
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return manifests / "index.json"


def test_match_signals_scores_exact_and_probable(tmp_path):
    module = load_module()
    manifest_index = write_manifest_fixture(tmp_path)
    clients, _, _ = module.load_manifest_clients(str(manifest_index))
    signals = [
        {
            "title": "Rede Um amplia operação em Porto Alegre RS",
            "title_normalized": "rede um amplia operacao em porto alegre rs",
            "url": "https://example.com/rede-um",
            "url_normalized": "https://example.com/rede-um",
            "published_at": "2026-08-10",
            "source": "Fonte A",
            "snippet": "Rede Um abre nova frente na praça.",
            "channel": "open",
            "evidence_kind": "news",
        },
        {
            "title": "Rede Um prepara expansão",
            "title_normalized": "rede um prepara expansao",
            "url": "https://example.com/rede-um-2",
            "url_normalized": "https://example.com/rede-um-2",
            "published_at": "2026-08-10",
            "source": "Fonte B",
            "snippet": "Expansão sem praça explícita.",
            "channel": "open",
            "evidence_kind": "news",
        },
    ]

    buckets = module.match_signals(signals, clients)

    assert len(buckets["matched_exact"]) == 1
    assert buckets["matched_exact"][0]["cliente_id"] == "client-1"
    assert len(buckets["matched_probable"]) == 1
    assert buckets["matched_probable"][0]["cliente_id"] == "client-1"


def test_match_signals_promotes_distinct_brand_alias_to_exact(tmp_path):
    module = load_module()
    assert module.title_starts_with_brand("bruda inaugura duas lojas", "bruda") is True
    assert module.title_starts_with_brand("rede bruda inaugura duas lojas", "bruda") is True
    assert module.title_starts_with_brand("banco central corta juros", "central") is False
    manifest_index = write_manifest_fixture(tmp_path)
    sellers_dir = manifest_index.parent / "sellers"
    manifest = json.loads((sellers_dir / "seller-1.json").read_text(encoding="utf-8"))
    manifest["clients"][0]["nome"] = "SUPERMERCADO BRUDA LTDA"
    manifest["clients"][0]["nome_fantasia"] = "CD BRUDA"
    manifest["clients"][0]["cidade"] = "Canoinhas"
    manifest["clients"][0]["uf"] = "SC"
    manifest["clients"][0]["aliases"] = [
        "supermercado bruda ltda",
        "cd bruda",
        "79645404000516",
        "canoinhas sc",
        "bruda",
    ]
    manifest["clients"][0]["brand_aliases"] = ["bruda"]
    (sellers_dir / "seller-1.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    clients, _, _ = module.load_manifest_clients(str(manifest_index))
    signals = [
        {
            "title": "Bruda inaugura duas novas lojas em uma semana",
            "title_normalized": "bruda inaugura duas novas lojas em uma semana",
            "url": "https://samais.com.br/publicacoes/rede-bruda-inaugura-duas-novas-lojas-em-uma-semana",
            "url_normalized": "https://samais.com.br/publicacoes/rede-bruda-inaugura-duas-novas-lojas-em-uma-semana",
            "published_at": "2026-08-05",
            "source": "samais",
            "snippet": "A rede Bruda inaugurou duas unidades em Rio Negrinho e passou a 12 operações em SC.",
            "channel": "open",
            "evidence_kind": "news",
        }
    ]

    buckets = module.match_signals(signals, clients)

    assert len(buckets["matched_exact"]) == 1
    assert buckets["matched_exact"][0]["cliente_id"] == "client-1"
    assert "brand_title_prefix:bruda" in buckets["matched_exact"][0]["match_reasons"]


def test_match_signals_does_not_promote_brand_seen_only_in_snippet(tmp_path):
    module = load_module()
    manifest_index = write_manifest_fixture(tmp_path)
    sellers_dir = manifest_index.parent / "sellers"
    manifest = json.loads((sellers_dir / "seller-1.json").read_text(encoding="utf-8"))
    manifest["clients"][0]["nome"] = "SUPERMERCADO BRUDA LTDA"
    manifest["clients"][0]["nome_fantasia"] = "CD BRUDA"
    manifest["clients"][0]["aliases"] = ["supermercado bruda ltda", "cd bruda", "bruda"]
    manifest["clients"][0]["brand_aliases"] = ["bruda"]
    (sellers_dir / "seller-1.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    clients, _, _ = module.load_manifest_clients(str(manifest_index))
    signals = [
        {
            "title": "Rede regional inaugura duas lojas em uma semana",
            "title_normalized": "rede regional inaugura duas lojas em uma semana",
            "url": "https://example.com/rede-regional-inaugura",
            "url_normalized": "https://example.com/rede-regional-inaugura",
            "published_at": "2026-08-05",
            "source": "example",
            "snippet": "A rede Bruda inaugurou duas novas unidades.",
            "channel": "open",
            "evidence_kind": "news",
        }
    ]

    buckets = module.match_signals(signals, clients)

    assert buckets["matched_exact"] == []
    assert buckets["matched_probable"] == []
    assert len(buckets["unmatched"]) == 1


def test_match_signals_avoids_substring_and_source_false_positives(tmp_path):
    module = load_module()
    manifest_index = write_manifest_fixture(tmp_path)
    sellers_dir = manifest_index.parent / "sellers"
    manifest = json.loads((sellers_dir / "seller-1.json").read_text(encoding="utf-8"))
    manifest["clients"][0]["nome"] = "DA ILHA SUPERMERCADO"
    manifest["clients"][0]["nome_fantasia"] = "DA ILHA"
    manifest["clients"][0]["aliases"] = ["da ilha supermercado", "da ilha", "ilha", "florianopolis sc"]
    manifest["clients"][0]["brand_aliases"] = ["ilha"]
    (sellers_dir / "seller-1.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    clients, _, _ = module.load_manifest_clients(str(manifest_index))
    signals = [
        {
            "title": "Caixa Seguridade vê lucro gerencial crescer 9,5% no 2° tri, para R$ 1,14 bi",
            "title_normalized": "caixa seguridade ve lucro gerencial crescer 9 5 no 2 tri para r 1 14 bi",
            "url": "https://valor.globo.com/financas/noticia/2026/08/10/caixa-seguridade-v-lucro-gerencial-crescer-95-pontos-percentuais-no-2-tri-para-r-114-b.ghtml",
            "url_normalized": "https://valor.globo.com/financas/noticia/2026/08/10/caixa-seguridade-v-lucro-gerencial-crescer-95-pontos-percentuais-no-2-tri-para-r-114-b.ghtml",
            "published_at": "2026-08-10",
            "source": "valor-economico",
            "snippet": "A Caixa Seguridade teve lucro gerencial de R$ 1,14 bilhão no segundo trimestre.",
            "channel": "crawler-brasil",
            "evidence_kind": "news",
        }
    ]

    buckets = module.match_signals(signals, clients)

    assert buckets["matched_exact"] == []
    assert buckets["matched_probable"] == []
    assert len(buckets["unmatched"]) == 1


def test_signal_match_cli_writes_publishable_and_skipped(tmp_path):
    manifest_index = write_manifest_fixture(tmp_path)
    signals_path = tmp_path / "signals.json"
    existing_path = tmp_path / "existing.json"
    out_dir = tmp_path / "out"

    signals_path.write_text(
        json.dumps(
            [
                {
                    "title": "Rede Um amplia operação em Porto Alegre RS",
                    "title_normalized": "rede um amplia operacao em porto alegre rs",
                    "url": "https://example.com/publish",
                    "url_normalized": "https://example.com/publish",
                    "published_at": "2026-08-10",
                    "source": "Fonte A",
                    "snippet": "Sinal fresco publicável.",
                    "channel": "open",
                    "evidence_kind": "news",
                },
                {
                    "title": "Rede Um reforça praça em Porto Alegre RS",
                    "title_normalized": "rede um reforca praca em porto alegre rs",
                    "url": "https://example.com/active",
                    "url_normalized": "https://example.com/active",
                    "published_at": "2026-08-10",
                    "source": "Fonte B",
                    "snippet": "Já ativa no histórico.",
                    "channel": "open",
                    "evidence_kind": "news",
                },
                {
                    "title": "Rede Um abriu novo espaço em Porto Alegre RS",
                    "title_normalized": "rede um abriu novo espaco em porto alegre rs",
                    "url": "https://example.com/stale",
                    "url_normalized": "https://example.com/stale",
                    "published_at": "2026-07-01",
                    "source": "Fonte C",
                    "snippet": "Velha demais para subir.",
                    "channel": "open",
                    "evidence_kind": "news",
                },
            ],
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    existing_path.write_text(
        json.dumps(
            [
                {
                    "id": "news-1",
                    "url": "https://example.com/active",
                    "cliente_id": "client-1",
                    "ativo": True,
                }
            ],
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--signals",
            str(signals_path),
            "--manifests-index",
            str(manifest_index),
            "--existing",
            str(existing_path),
            "--out-dir",
            str(out_dir),
            "--today",
            "2026-08-11",
            "--max-age-days",
            "10",
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=60,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["publishable"] == 1
    assert summary["skip_active"] == 1
    assert summary["skip_stale"] == 1

    publishable = json.loads((out_dir / "prepared" / "pre_llm_publishable.json").read_text(encoding="utf-8"))
    assert publishable[0]["cliente_id"] == "client-1"
    assert publishable[0]["client_context"] == {
        "cliente_id": "client-1",
        "nome": "Rede Um Ltda",
        "nome_fantasia": "Rede Um",
        "cidade": "Porto Alegre",
        "uf": "RS",
        "tabela_atual": "191 - REDE UM",
        "rfm_label": "A",
        "access_types": ["titular"],
        "brand_aliases": [],
    }
    skipped = json.loads((out_dir / "prepared" / "skipped.json").read_text(encoding="utf-8"))
    assert len(skipped["already_active"]) == 1
    assert len(skipped["stale"]) == 1
    by_seller = json.loads((out_dir / "matched" / "per_seller" / "index.json").read_text(encoding="utf-8"))
    assert "seller-1" in by_seller
