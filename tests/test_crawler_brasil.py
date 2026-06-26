"""Testes unitários e smoke tests para excrtx-crawler-brasil."""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Adiciona o diretório tools/ ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.excrtx_crawler_brasil.sources import get_sources, get_source, CPG_SOURCES, Source
from tools.excrtx_crawler_brasil.crawler import (
    CrawlerBrasil, Cache, parse_rss, make_item, _strip_html, _parse_date,
)


# ── Fontes ──────────────────────────────────────────────────────────────────

class TestSources:
    def test_cpg_sources_count(self):
        """Deve haver pelo menos 5 fontes CPG."""
        cpg = get_sources(["cpg"])
        assert len(cpg) >= 5, f"Esperado >=5 fontes CPG, encontrado {len(cpg)}"

    def test_all_sources_count(self):
        """Deve haver pelo menos 12 fontes no total."""
        all_s = get_sources(None)
        assert len(all_s) >= 12

    def test_get_source_by_slug(self):
        s = get_source("exame")
        assert s is not None
        assert s.name == "Exame"
        assert s.source_type == "rss"

    def test_get_source_not_found(self):
        assert get_source("fonte-inexistente") is None

    def test_filter_by_domain(self):
        alimentos = get_sources(["alimentos"])
        slugs = [s.slug for s in alimentos]
        assert "food-connection" in slugs

    def test_all_have_urls(self):
        for s in CPG_SOURCES:
            assert s.url.startswith("http"), f"URL inválida para {s.slug}"


# ── Parsers ─────────────────────────────────────────────────────────────────

SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <item>
      <title>Notícia de Teste</title>
      <link>https://example.com/noticia</link>
      <pubDate>Wed, 25 Jun 2026 10:00:00 GMT</pubDate>
      <description><![CDATA[Descrição da <b>notícia</b> de teste com HTML.]]></description>
    </item>
    <item>
      <title>Outra Notícia</title>
      <link>https://example.com/outra</link>
      <pubDate>Wed, 25 Jun 2026 09:00:00 GMT</pubDate>
      <description>Segunda notícia</description>
    </item>
  </channel>
</rss>"""

SAMPLE_ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Test Atom</title>
  <entry>
    <title>Atom Entry</title>
    <link rel="alternate" href="https://example.com/atom-entry"/>
    <published>2026-06-25T10:00:00Z</published>
    <summary>Atom summary text</summary>
  </entry>
</feed>"""


class TestParseRSS:
    def test_parse_rss_basic(self):
        source = get_source("exame")
        items = parse_rss(SAMPLE_RSS, source)
        assert len(items) == 2
        assert items[0]["title"] == "Notícia de Teste"
        assert items[0]["url"] == "https://example.com/noticia"
        assert items[0]["source"] == "exame"
        assert items[0]["date"] == "2026-06-25"

    def test_parse_rss_html_stripped(self):
        source = get_source("exame")
        items = parse_rss(SAMPLE_RSS, source)
        assert "<b>" not in items[0]["snippet"]
        assert "notícia" in items[0]["snippet"]

    def test_parse_atom(self):
        source = get_source("exame")
        items = parse_rss(SAMPLE_ATOM, source)
        assert len(items) >= 1
        assert items[0]["title"] == "Atom Entry"

    def test_parse_empty(self):
        source = get_source("exame")
        items = parse_rss("", source)
        assert items == []

    def test_parse_malformed(self):
        source = get_source("exame")
        items = parse_rss("not xml at all", source)
        assert items == []


class TestHelpers:
    def test_strip_html(self):
        assert _strip_html("<p>Hello <b>World</b></p>") == "Hello World"

    def test_parse_date_rfc2822(self):
        assert _parse_date("Wed, 25 Jun 2026 10:00:00 GMT") == "2026-06-25"

    def test_parse_date_empty(self):
        assert _parse_date("") == ""

    def test_make_item_schema(self):
        item = make_item("Título", "https://example.com", "2026-06-25", "teste", "snippet", "economia")
        required = ["title", "url", "date", "source", "snippet", "domain", "retrieved_at"]
        assert all(k in item for k in required)
        assert item["title"] == "Título"


# ── Cache ───────────────────────────────────────────────────────────────────

class TestCache:
    def test_cache_set_get(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            c = Cache(tmpdir)
            c.set("url1", "content1")
            assert c.get("url1") == "content1"

    def test_cache_miss(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            c = Cache(tmpdir)
            assert c.get("nonexistent") is None


# ── Smoke tests (requerem rede) ─────────────────────────────────────────────

@pytest.mark.slow
class TestSmokeCrawler:
    def test_crawl_cpg_returns_items(self):
        """Smoke: crawler coleta itens reais do domínio CPG."""
        crawler = CrawlerBrasil()
        sources = get_sources(["cpg"])[:3]  # 3 fontes para não demorar
        items = crawler.crawl_sync(sources, limit_per_source=3)
        assert len(items) >= 1, "Deve retornar pelo menos 1 item"
        for item in items:
            assert item["title"], "Título não pode ser vazio"
            assert item["url"].startswith("http"), f"URL inválida: {item['url']}"
            assert item["source"], "Source não pode ser vazio"

    def test_crawl_multiple_sources(self):
        """Smoke: crawler coleta de >=3 fontes diferentes."""
        crawler = CrawlerBrasil()
        sources = get_sources(["cpg"])[:4]
        items = crawler.crawl_sync(sources, limit_per_source=3)
        unique_sources = set(i["source"] for i in items)
        assert len(unique_sources) >= 2, f"Esperado >=2 fontes, encontrado {unique_sources}"

    def test_output_is_valid_json(self):
        """Smoke: output é JSON parseável."""
        crawler = CrawlerBrasil()
        sources = get_sources(["cpg"])[:2]
        items = crawler.crawl_sync(sources, limit_per_source=2)
        # Consegue serializar e desserializar
        dumped = json.dumps(items, ensure_ascii=False)
        reloaded = json.loads(dumped)
        assert reloaded == items


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
