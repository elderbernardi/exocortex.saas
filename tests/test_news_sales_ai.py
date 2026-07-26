"""Testes estruturais e unitários para excrtx-news-sales-ai."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / "skills" / "excrtx-news-sales-ai"
SCRIPT = SKILL_DIR / "scripts" / "build_dossier.py"
STEP = REPO_ROOT / "setup" / "step-03-install-skills.sh"


def load_module():
    spec = importlib.util.spec_from_file_location("build_dossier", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_script(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=60,
    )


class TestStructural:
    def test_skill_files_exist(self):
        assert (SKILL_DIR / "SKILL.md").exists()
        assert (SKILL_DIR / "references" / "route-b-architecture.md").exists()
        assert SCRIPT.exists()

    def test_help_works(self):
        result = run_script("--help")
        assert result.returncode == 0, result.stdout + result.stderr
        assert "--job-context" in result.stdout
        assert "--crawler" in result.stdout

    def test_installer_copies_skill_recursively(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            hermes_home = root / "hermes"
            exocortex_home = root / "exocortex"
            acervo = exocortex_home / "acervo"

            env = os.environ.copy()
            env.update(
                {
                    "HERMES_HOME": str(hermes_home),
                    "EXOCORTEX_HOME": str(exocortex_home),
                    "ACERVO": str(acervo),
                }
            )

            result = subprocess.run(
                ["bash", str(STEP)],
                cwd=REPO_ROOT,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            assert result.returncode == 0, result.stdout + "\n" + result.stderr

            installed_root = hermes_home / "skills" / "excrtx" / "excrtx-news-sales-ai"
            assert (installed_root / "SKILL.md").exists()
            assert (installed_root / "scripts" / "build_dossier.py").exists()
            assert (installed_root / "references" / "route-b-architecture.md").exists()


class TestNormalization:
    def test_normalize_crawler_items(self):
        module = load_module()
        payload = [
            {
                "title": "Rede Exemplo amplia operação no Sul",
                "url": "https://example.com/noticia?utm_source=feed&id=123",
                "date": "2026-07-24",
                "source": "valor-economico",
                "snippet": "Expansão regional.",
                "domain": "cpg",
            }
        ]
        items = module.normalize_crawler_items(payload)
        assert items[0]["url_normalized"] == "https://example.com/noticia?id=123"
        assert items[0]["channel"] == "crawler-brasil"

    def test_normalize_agent_reach_items_accepts_flexible_keys(self):
        module = load_module()
        payload = [
            {
                "title": "Sinal web",
                "link": "https://example.com/web?fbclid=abc",
                "date": "2026-07-23T10:00:00Z",
                "site": "web-search",
                "summary": "Resumo externo.",
                "channel": "web",
            }
        ]
        items = module.normalize_agent_reach_items(payload)
        assert items[0]["source"] == "web-search"
        assert items[0]["published_at"] == "2026-07-23"
        assert items[0]["url_normalized"] == "https://example.com/web"

    def test_normalize_docbrain_items_builds_acervo_reference(self):
        module = load_module()
        payload = [
            {
                "ok": True,
                "title": "Relatório Girando Sol",
                "relative_output": "micro/demo/knowledge/relatorio.md",
                "summary_excerpt": "Receita avançou.",
                "sections_count": 4,
                "tables_count": 1,
            }
        ]
        docs = module.normalize_docbrain_items(payload)
        assert docs == [
            {
                "title": "Relatório Girando Sol",
                "reference": "acervo://micro/demo/knowledge/relatorio.md",
                "microverso": None,
                "summary_excerpt": "Receita avançou.",
                "sections_count": 4,
                "tables_count": 1,
                "document_id": None,
            }
        ]


class TestDossier:
    def test_build_dossier_macro(self):
        module = load_module()
        job_context = {
            "schema": "projetob/news-job-context/v1",
            "scope": "macro",
            "research_context": {
                "sector_slug": "limpeza-domestica",
                "region": "sul-brasil",
                "query_terms": ["varejo", "limpeza"],
            },
            "internal_context": {},
        }
        dossier = module.build_dossier(
            job_context,
            crawler_payloads=[[{
                "title": "Rede Exemplo amplia operação no Sul",
                "url": "https://example.com/noticia?utm_source=feed",
                "date": "2026-07-24",
                "source": "valor-economico",
                "snippet": "Expansão regional.",
            }]],
            agent_reach_payloads=[[{
                "title": "Rede Exemplo amplia operação no Sul",
                "url": "https://example.com/noticia",
                "published_at": "2026-07-24",
                "source": "google-news",
                "snippet": "Mesmo fato em outro canal.",
            }]],
            docbrain_payloads=[],
            max_signals=10,
        )
        assert dossier["schema"] == "exocortex/news-route-b-dossier/v1"
        assert dossier["focus"]["scope"] == "macro"
        assert dossier["source_counts"]["signals_after_dedupe"] == 1
        assert dossier["prompt_packet"]["writer_contract"]["tool"] == "sales-ai.publish_noticia"

    def test_build_dossier_micro_preserves_client_context(self):
        module = load_module()
        job_context = {
            "schema": "projetob/news-job-context/v1",
            "scope": "micro",
            "research_context": {
                "sector_slug": "limpeza-domestica",
                "region": "sul-brasil",
                "public_client_name": "Rede Exemplo",
                "query_terms": ["sortimento", "expansão"],
            },
            "internal_context": {
                "cliente_id": "00000000-0000-4000-8000-000000000001",
                "seller_id": "00000000-0000-4000-8000-000000000002",
            },
        }
        dossier = module.build_dossier(
            job_context,
            crawler_payloads=[],
            agent_reach_payloads=[],
            docbrain_payloads=[[{
                "ok": True,
                "title": "Relatório Girando Sol",
                "relative_output": "micro/demo/knowledge/relatorio.md",
                "summary_excerpt": "Receita avançou.",
            }]],
            max_signals=10,
        )
        assert dossier["focus"]["public_client_name"] == "Rede Exemplo"
        assert dossier["focus"]["cliente_id"] == "00000000-0000-4000-8000-000000000001"
        assert dossier["documents"][0]["reference"] == "acervo://micro/demo/knowledge/relatorio.md"
        constraints = " ".join(dossier["prompt_packet"]["constraints"])
        assert "cliente-alvo" in constraints

    def test_build_dossier_accepts_orchestrated_research_wrappers(self):
        module = load_module()
        context = {
            "schema": "projetob/news-job-context/v1",
            "scope": "macro",
            "research_context": {"sector_slug": "varejo", "region": "sul-brasil", "query_terms": ["varejo"]},
            "internal_context": {},
        }
        research = {
            "crawler_br": {"count": 1, "items": [{
                "title": "Canal amplia operação", "url": "https://example.com/crawler",
                "date": "2026-07-26", "source": "crawler", "snippet": "Expansão regional.",
            }]},
            "agent_reach": {"count": 1, "items": [{
                "title": "Mercado ajusta preços", "url": "https://example.com/reach",
                "published_at": "2026-07-26", "source": "reach", "snippet": "Movimento de mercado.",
            }]},
        }
        dossier = module.build_dossier(
            context,
            crawler_payloads=[research],
            agent_reach_payloads=[research],
            docbrain_payloads=[],
            max_signals=10,
        )
        assert dossier["source_counts"]["crawler_brasil"] == 1
        assert dossier["source_counts"]["agent_reach"] == 1
        assert dossier["source_counts"]["signals_after_dedupe"] == 2

    def test_cli_writes_json_file(self, tmp_path):
        job_context = tmp_path / "context.json"
        crawler = tmp_path / "crawler.json"
        output = tmp_path / "dossier.json"
        job_context.write_text(json.dumps({
            "schema": "projetob/news-job-context/v1",
            "scope": "macro",
            "research_context": {"sector_slug": "limpeza-domestica", "region": "sul-brasil", "query_terms": ["varejo"]},
            "internal_context": {},
        }), encoding="utf-8")
        crawler.write_text(json.dumps([
            {
                "title": "Título",
                "url": "https://example.com/a?utm_source=feed",
                "date": "2026-07-24",
                "source": "valor-economico",
                "snippet": "Resumo",
            }
        ]), encoding="utf-8")

        result = run_script(
            "--job-context", str(job_context),
            "--crawler", str(crawler),
            "--output-file", str(output),
        )
        assert result.returncode == 0, result.stdout + result.stderr
        payload = json.loads(output.read_text(encoding="utf-8"))
        assert payload["schema"] == "exocortex/news-route-b-dossier/v1"
        assert payload["signals"][0]["url_normalized"] == "https://example.com/a"
