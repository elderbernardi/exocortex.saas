"""Testes de integração para excrtx-research-cpg-brasil."""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ORCHESTRATE = Path(__file__).resolve().parents[1] / "skills" / "excrtx-research-cpg-brasil" / "scripts" / "orchestrate.py"
REPO_ROOT = Path(__file__).resolve().parents[1]


def run_orchestrate(*args) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ORCHESTRATE)] + list(args),
        capture_output=True, text=True, timeout=120,
        cwd=str(REPO_ROOT),
    )


# ── Testes estruturais ──────────────────────────────────────────────────────

class TestStructural:
    def test_skill_md_exists(self):
        skill_md = REPO_ROOT / "skills" / "excrtx-research-cpg-brasil" / "SKILL.md"
        assert skill_md.exists(), "SKILL.md não encontrado"

    def test_orchestrate_exists(self):
        assert ORCHESTRATE.exists(), "orchestrate.py não encontrado"

    def test_templates_exist(self):
        templates = REPO_ROOT / "skills" / "excrtx-research-cpg-brasil" / "references" / "query-templates.md"
        assert templates.exists(), "query-templates.md não encontrado"

    def test_help_works(self):
        result = run_orchestrate("--help")
        assert result.returncode == 0

    def test_list_templates(self):
        result = run_orchestrate("--help")
        assert "panorama" in result.stdout
        assert "varejo" in result.stdout


# ── Smoke tests (requerem rede, usam --skip-l30d) ──────────────────────────

@pytest.mark.slow
class TestSmokeOrchestrator:
    def test_varejo_skip_l30d_returns_valid_briefing(self):
        """Smoke: template varejo sem last30days retorna briefing válido."""
        result = run_orchestrate("--template", "varejo", "--skip-l30d")
        assert result.returncode == 0

        output = result.stdout
        # Contrato: badge + O que aprendemos + PADRÕES-CHAVE + emoji-footer
        assert "📊 CPG Brasil" in output, "Badge ausente"
        assert "O que aprendemos" in output, "Seção de insights ausente"
        assert "PADRÕES-CHAVE" in output, "Seção de padrões ausente"
        assert "✅" in output, "Emoji-footer ausente"
        assert "crawler-brasil" in output, "Fonte crawler não mencionada"

    def test_limpeza_skip_l30d_returns_items(self):
        """Smoke: template limpeza retorna itens reais."""
        result = run_orchestrate("--template", "limpeza", "--skip-l30d")
        assert result.returncode == 0
        # Deve ter itens do crawler ou agent-reach
        assert "crawler-brasil" in result.stdout or "agent-reach" in result.stdout

    def test_json_output(self):
        """Smoke: output JSON é parseável."""
        result = run_orchestrate("--template", "varejo", "--skip-l30d", "--output", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "synthesis" in data
        assert "template" in data
        assert data["template"] == "varejo"
        assert isinstance(data["crawler_br"]["count"], int)
        assert data["crawler_br"]["count"] >= 0

    def test_all_templates_work(self):
        """Smoke: todos os templates rodam sem erro."""
        for template in ["panorama", "inovacao", "supply"]:
            result = run_orchestrate("--template", template, "--skip-l30d")
            assert result.returncode == 0, f"Template {template} falhou"
            assert "O que aprendemos" in result.stdout

    def test_output_in_portuguese(self):
        """Smoke: output está em PT-BR."""
        result = run_orchestrate("--template", "varejo", "--skip-l30d")
        pt_markers = ["O que aprendemos", "PADRÕES-CHAVE", "Cobertura setorial"]
        for marker in pt_markers:
            assert marker in result.stdout, f"Marcador PT-BR '{marker}' ausente"


# ── Testes de síntese ───────────────────────────────────────────────────────

class TestSynthesis:
    def test_synthesis_with_empty_data(self):
        """Síntese não quebra com dados vazios."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "orchestrate",
            REPO_ROOT / "skills" / "excrtx-research-cpg-brasil" / "scripts" / "orchestrate.py"
        )
        orchestrate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(orchestrate)

        result = orchestrate.synthesize("varejo", orchestrate.TEMPLATES["varejo"], None, [], [])
        assert "Nenhum sinal relevante" in result or "O que aprendemos" in result

    def test_synthesis_with_crawler_data(self):
        """Síntese processa dados do crawler corretamente."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "orchestrate",
            REPO_ROOT / "skills" / "excrtx-research-cpg-brasil" / "scripts" / "orchestrate.py"
        )
        orchestrate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(orchestrate)

        cr_items = [
            {"title": "Notícia teste", "url": "https://ex.com", "date": "2026-06-25",
             "source": "valor-economico", "snippet": "Resumo da notícia"}
        ]
        result = orchestrate.synthesize("panorama", orchestrate.TEMPLATES["panorama"], None, [], cr_items)
        assert "Notícia teste" in result
        assert "valor-economico" in result
        assert "https://ex.com" in result

    def test_synthesis_includes_docbrain_structured_source(self):
        """Síntese menciona documentos promovidos via DocBrain."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "orchestrate",
            REPO_ROOT / "skills" / "excrtx-research-cpg-brasil" / "scripts" / "orchestrate.py"
        )
        orchestrate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(orchestrate)

        docbrain_payloads = [{
            "ok": True,
            "title": "Relatório Girando Sol",
            "relative_output": "micro/girando-sol/knowledge/relatorio-girando-sol.md",
            "sections_count": 12,
            "tables_count": 3,
            "summary_excerpt": "Receita líquida avançou no trimestre.",
            "microverso": "girando-sol",
        }]
        result = orchestrate.synthesize(
            "panorama",
            orchestrate.TEMPLATES["panorama"],
            None,
            [],
            [],
            docbrain_payloads=docbrain_payloads,
        )
        assert "[docbrain]" in result
        assert "Relatório Girando Sol" in result
        assert "micro/girando-sol/knowledge/relatorio-girando-sol.md" in result
        assert "Documentos promovidos" in result
        assert "📄 docbrain" in result

    def test_main_json_output_includes_docbrain_structured_sources(self, monkeypatch, tmp_path, capsys):
        """CLI JSON expõe structured_sources.docbrain quando há documentos."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "orchestrate",
            REPO_ROOT / "skills" / "excrtx-research-cpg-brasil" / "scripts" / "orchestrate.py"
        )
        orchestrate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(orchestrate)

        sample_doc = tmp_path / "sample.md"
        sample_doc.write_text("# Documento\n", encoding="utf-8")

        monkeypatch.setattr(orchestrate, "run_agent_reach", lambda template: [])
        monkeypatch.setattr(orchestrate, "run_crawler", lambda template: [])
        monkeypatch.setattr(orchestrate, "run_last30days", lambda template, days=30: None)
        monkeypatch.setattr(
            orchestrate,
            "run_docbrain_adapter",
            lambda *args, **kwargs: [{
                "ok": True,
                "title": "Documento teste",
                "relative_output": "micro/demo/knowledge/documento-teste.md",
                "sections_count": 2,
                "tables_count": 1,
                "summary_excerpt": "Linha principal.",
                "microverso": "demo",
            }],
        )
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "orchestrate.py",
                "--template", "panorama",
                "--skip-l30d",
                "--output", "json",
                "--document", str(sample_doc),
                "--document-microverso", "demo",
            ],
        )

        exit_code = asyncio.run(orchestrate.main())
        captured = capsys.readouterr()
        assert exit_code == 0
        payload = json.loads(captured.out)
        assert payload["structured_sources"]["docbrain"][0]["relative_output"] == "micro/demo/knowledge/documento-teste.md"
        assert "[docbrain]" in payload["synthesis"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
