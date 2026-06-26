"""
Crawler assíncrono para fontes setoriais brasileiras.

Suporta RSS (feedparser), APIs JSON e HTML leve (BeautifulSoup).
Com rate limiting por domínio, cache local e output normalizado.
"""

import asyncio
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse
from xml.etree import ElementTree

import httpx

from .sources import Source


# ── Schema de saída ─────────────────────────────────────────────────────────

def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def make_item(
    title: str,
    url: str,
    date: str,
    source: str,
    snippet: str = "",
    domain: str = "",
) -> dict:
    return {
        "title": title.strip()[:300],
        "url": url.strip(),
        "date": date,
        "source": source,
        "snippet": snippet.strip()[:500] if snippet else "",
        "domain": domain,
        "retrieved_at": now_utc(),
    }


# ── Cache local ─────────────────────────────────────────────────────────────

class Cache:
    """Cache simples em disco para evitar requests repetidos."""

    def __init__(self, cache_dir: str = "/tmp/excrtx-crawler-cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key(self, url: str) -> str:
        return hashlib.sha256(url.encode()).hexdigest()[:16]

    def get(self, url: str) -> Optional[str]:
        path = self.cache_dir / self._key(url)
        if not path.exists():
            return None
        age = time.time() - path.stat().st_mtime
        if age > 900:  # 15 min default TTL
            path.unlink(missing_ok=True)
            return None
        return path.read_text()

    def set(self, url: str, content: str):
        path = self.cache_dir / self._key(url)
        path.write_text(content)


# ── Parsers ─────────────────────────────────────────────────────────────────

def parse_rss(xml_content: str, source: Source) -> List[dict]:
    """Parseia feed RSS/Atom e retorna itens normalizados."""
    items = []
    try:
        root = ElementTree.fromstring(xml_content)
    except ElementTree.ParseError:
        return items

    # Suporta RSS 2.0 e Atom
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall(".//item") or root.findall(".//atom:entry", ns)

    for entry in entries:
        title = (
            entry.findtext("title") or
            entry.findtext("atom:title", namespaces=ns) or ""
        )
        link = (
            entry.findtext("link") or
            _find_atom_link(entry, ns) or ""
        )
        pub_date = (
            entry.findtext("pubDate") or
            entry.findtext("published") or
            entry.findtext("atom:updated", namespaces=ns) or ""
        )
        description = (
            entry.findtext("description") or
            entry.findtext("summary") or
            entry.findtext("atom:summary", namespaces=ns) or ""
        )

        # Limpa HTML do description
        snippet = _strip_html(description)[:500]

        # Converte data para ISO
        date_iso = _parse_date(pub_date)

        if title and link:
            items.append(make_item(
                title=title,
                url=link,
                date=date_iso,
                source=source.slug,
                snippet=snippet,
                domain=", ".join(source.domains),
            ))

    return items


def _find_atom_link(entry, ns: dict) -> str:
    """Extrai href de link Atom."""
    for link in entry.findall("atom:link", ns):
        href = link.get("href", "")
        rel = link.get("rel", "alternate")
        if rel == "alternate" and href:
            return href
    return ""


def _strip_html(text: str) -> str:
    """Remove tags HTML básicas."""
    import re
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _parse_date(date_str: str) -> str:
    """Converte datas comuns de RSS para ISO 8601."""
    if not date_str:
        return ""
    from email.utils import parsedate_to_datetime
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return date_str[:10] if len(date_str) >= 10 else date_str


# ── HTML Parser ─────────────────────────────────────────────────────────────

def parse_html_listing(html_content: str, source: Source) -> List[str]:
    """Extrai URLs de artigos de uma página de listagem HTML (ex: /noticias/).

    Para ScannTech: extrai links <a> dentro de cards de notícias.
    Retorna lista de URLs absolutas de artigos.
    """
    import re

    urls: set[str] = set()
    base = f"https://{urlparse(source.url).netloc}"

    if source.slug == "scanntech":
        # ScannTech: links na página /noticias/ com padrão /slug-do-artigo/
        # Exclui páginas institucionais: sobre/, mapa-do-site/, central-de-privacidade, solucoes/
        pattern = re.findall(
            r'<a[^>]*href="(https://www\.scanntech\.com\.br/(?!'
            r'noticias|solucoes|central|sobre|mapa-do-site|contato|trabalhe|politica|wp-'
            r')[^"]+)"',
            html_content, re.I,
        )
        for url in pattern:
            if url not in urls and len(url) > 50:
                urls.add(url)
    else:
        # Genérico: busca links com padrão de artigo (contendo ano/mês ou slug)
        pattern = re.findall(
            r'<a[^>]*href="(/[^"]*(?:20[2-9]\d/[^"]+/\w+|noticia[^"]+|artigo[^"]+))"',
            html_content, re.I,
        )
        for path in pattern:
            full_url = path if path.startswith("http") else base + path
            urls.add(full_url)

    return list(urls)


def parse_html_article(html_content: str, url: str, source: Source) -> Optional[dict]:
    """Extrai título, data e snippet de uma página de artigo HTML."""
    import re

    title = ""
    pub_date = ""
    snippet = ""

    if source.slug == "scanntech":
        # ScannTech: meta published_time, h1, content
        title_match = re.search(r"<h1[^>]*>(.*?)</h1>", html_content, re.I | re.DOTALL)
        if title_match:
            title = _strip_html(title_match.group(1))
        date_match = re.search(
            r'<meta[^>]*property="article:published_time"[^>]*content="([^"]+)"',
            html_content, re.I,
        )
        if date_match:
            pub_date = date_match.group(1)[:10]
        desc_match = re.search(
            r'<meta[^>]*name="description"[^>]*content="([^"]+)"',
            html_content, re.I,
        )
        if desc_match:
            snippet = desc_match.group(1)[:500]

    elif source.slug == "nielsen":
        # Nielsen: h1, meta description, sitemap date
        title_match = re.search(r"<h1[^>]*>(.*?)</h1>", html_content, re.I | re.DOTALL)
        if title_match:
            title = _strip_html(title_match.group(1)).replace(" | Nielsen", "")
        # Nielsen doesn't expose publish date in meta — use the URL year
        year_match = re.search(r"/insights/(20\d{2})/", url)
        if year_match:
            pub_date = year_match.group(1)
        desc_match = re.search(
            r'<meta[^>]*name="description"[^>]*content="([^"]+)"',
            html_content, re.I,
        )
        if desc_match:
            snippet = desc_match.group(1)[:500]

    else:
        # Genérico
        title_match = re.search(r"<title>(.*?)</title>", html_content, re.I | re.DOTALL)
        if title_match:
            title = _strip_html(title_match.group(1))
        desc_match = re.search(
            r'<meta[^>]*name="description"[^>]*content="([^"]+)"',
            html_content, re.I,
        )
        if desc_match:
            snippet = desc_match.group(1)[:500]

    if not title:
        return None

    return make_item(
        title=title[:300],
        url=url,
        date=pub_date,
        source=source.slug,
        snippet=snippet,
        domain=", ".join(source.domains),
    )


def parse_sitemap(xml_content: str) -> List[str]:
    """Extrai URLs de um sitemap XML. Suporta sitemapindex e urlset."""
    urls = []
    try:
        root = ElementTree.fromstring(xml_content)
    except ElementTree.ParseError:
        return urls

    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    # Pode ser um sitemap index ou urlset
    for loc in root.findall(".//sm:loc", ns):
        if loc.text:
            urls.append(loc.text.strip())
    return urls


def parse_api_json(json_content: str, source: Source) -> List[dict]:
    """Parseia resposta JSON de API (ex: WP REST) e retorna itens normalizados."""
    items = []
    try:
        data = json.loads(json_content)
    except json.JSONDecodeError:
        return items

    posts = data if isinstance(data, list) else []

    for post in posts:
        title_raw = post.get("title", {})
        if isinstance(title_raw, dict):
            title = _strip_html(title_raw.get("rendered", ""))
        else:
            title = str(title_raw)

        excerpt_raw = post.get("excerpt", {})
        if isinstance(excerpt_raw, dict):
            snippet = _strip_html(excerpt_raw.get("rendered", ""))[:500]
        else:
            snippet = ""

        url = post.get("link", "")
        pub_date = (post.get("date") or "")[:10]

        if title and url:
            items.append(make_item(
                title=title[:300],
                url=url,
                date=pub_date,
                source=source.slug,
                snippet=snippet,
                domain=", ".join(source.domains),
            ))

    return items


def parse_browser(url: str, source: Source, limit: int = 10) -> List[dict]:
    """Usa Playwright para extrair artigos de sites com renderização JavaScript.

    Navega até a URL, espera o JS renderizar, extrai links de artigos via
    JavaScript evaluation, depois lê cada artigo via Jina Reader.
    """
    items = []
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return items

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, timeout=source.timeout_seconds * 1000, wait_until="networkidle")
            page.wait_for_timeout(3000)  # extra 3s for dynamic content

            if source.slug == "supervarejo":
                items = _extract_supervarejo(page, source, limit)
            else:
                # Genérico: extrai links com texto significativo
                items = _extract_generic_browser(page, source, limit)

        except Exception:
            pass
        finally:
            browser.close()

    return items


def _extract_supervarejo(page, source: Source, limit: int) -> List[dict]:
    """Extrator específico para SuperVarejo."""
    import re
    items = []
    links = page.evaluate("""() => {
        const links = [...document.querySelectorAll('a')]
            .filter(a => a.textContent.trim().length > 30)
            .map(a => ({
                href: a.href,
                text: a.textContent.trim()
            }));
        // Remove duplicates by href
        const seen = new Set();
        return links.filter(l => {
            if (seen.has(l.href) || !l.href.includes('supervarejo.com.br'))
                return false;
            seen.add(l.href);
            return true;
        });
    }""")

    for link in links[:limit * 2]:  # fetch more to account for noise
        text = link["text"]
        href = link["href"]

        # Padrão: "Categoria\n DATA\n Título" ou similar
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        # Remove "leia mais", "Cadastre-se", etc.
        content_lines = [
            l for l in lines
            if l.lower() not in ("leia", "mais", "cadastre-se", "faça login", "leia mais")
            and len(l) > 3
        ]

        if len(content_lines) >= 2:
            # Última linha significativa é o título
            title = content_lines[-1] if len(content_lines[-1]) > 15 else (content_lines[-2] if len(content_lines) > 1 else "")
            # Procura data (padrão "DD de mês de AAAA")
            date = ""
            for line in content_lines:
                date_match = re.search(r"(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})", line)
                if date_match:
                    months = {"janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04",
                              "maio": "05", "junho": "06", "julho": "07", "agosto": "08",
                              "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"}
                    m = months.get(date_match.group(2).lower(), "01")
                    date = f"{date_match.group(3)}-{m}-{date_match.group(1).zfill(2)}"
                    break

            if title and href and "supervarejo.com.br" in href:
                items.append(make_item(
                    title=title[:300],
                    url=href,
                    date=date,
                    source=source.slug,
                    snippet="",
                    domain=", ".join(source.domains),
                ))

    return items[:limit]


def _extract_generic_browser(page, source: Source, limit: int) -> List[dict]:
    """Extrator genérico para sites JS."""
    links = page.evaluate("""() => {
        return [...document.querySelectorAll('a')]
            .filter(a => a.textContent.trim().length > 25 && a.href)
            .map(a => ({href: a.href, text: a.textContent.trim().substring(0, 200)}))
            .slice(0, 30);
    }""")

    items = []
    seen = set()
    for link in links:
        if link["href"] in seen:
            continue
        seen.add(link["href"])
        items.append(make_item(
            title=link["text"][:300],
            url=link["href"],
            date="",
            source=source.slug,
            snippet="",
            domain=", ".join(source.domains),
        ))
    return items[:limit]


# ── Orquestrador ────────────────────────────────────────────────────────────

class CrawlerBrasil:
    """Orquestrador de coleta em fontes brasileiras."""

    def __init__(self, cache_dir: str = "/tmp/excrtx-crawler-cache"):
        self.cache = Cache(cache_dir)
        self._last_request: dict[str, float] = {}  # domínio → timestamp

    async def _fetch(self, client: httpx.AsyncClient, source: Source) -> Optional[str]:
        """Busca conteúdo de uma fonte com rate limiting e cache."""

        # Cache hit?
        cached = self.cache.get(source.url)
        if cached:
            return cached

        # Rate limiting por domínio
        domain = urlparse(source.url).netloc
        elapsed = time.time() - self._last_request.get(domain, 0)
        if elapsed < source.rate_limit_seconds:
            await asyncio.sleep(source.rate_limit_seconds - elapsed)

        try:
            response = await client.get(
                source.url,
                follow_redirects=True,
                timeout=source.timeout_seconds,
                headers={"User-Agent": "Exocortex-CrawlerBrasil/1.0"},
            )
            self._last_request[domain] = time.time()

            if response.status_code == 200:
                content = response.text
                self.cache.set(source.url, content)
                return content
        except Exception:
            pass

        return None

    async def crawl(
        self,
        sources: List[Source],
        limit_per_source: int = 15,
    ) -> List[dict]:
        """Coleta itens de fontes HTTP em paralelo (RSS, API, sitemap, HTML)."""
        all_items: List[dict] = []

        async with httpx.AsyncClient() as client:
            tasks = [self._fetch(client, s) for s in sources]
            results = await asyncio.gather(*tasks)

            for source, content in zip(sources, results):
                if not content:
                    continue

                if source.source_type == "rss":
                    items = parse_rss(content, source)
                    all_items.extend(items[:limit_per_source])

                elif source.source_type == "api":
                    items = parse_api_json(content, source)
                    all_items.extend(items[:limit_per_source])

                elif source.source_type == "sitemap":
                    # Nível 1: sitemap index → extrai URLs de sub-sitemaps
                    sub_sitemap_urls = parse_sitemap(content)
                    # Filtra apenas sub-sitemaps relevantes (insight)
                    insight_sitemaps = [
                        u for u in sub_sitemap_urls
                        if "insight-sitemap" in u and u.endswith(".xml")
                    ]
                    # Nível 2: cada sub-sitemap → extrai URLs de artigos
                    article_urls = []
                    for sitemap_url in insight_sitemaps[:5]:  # max 5 sub-sitemaps
                        sitemap_xml = await self._fetch(client, Source(
                            slug=source.slug + "-sitemap",
                            name=source.name,
                            source_type="html",
                            url=sitemap_url,
                            domains=source.domains,
                            description=source.description,
                        ))
                        if sitemap_xml:
                            article_urls.extend(parse_sitemap(sitemap_xml))
                    # Filtra apenas artigos PT-BR
                    pt_urls = [u for u in article_urls if "/pt/insights/" in u]
                    for article_url in pt_urls[:limit_per_source]:
                        html = await self._fetch(client, Source(
                            slug=source.slug,
                            name=source.name,
                            source_type="html",
                            url=article_url,
                            domains=source.domains,
                            description=source.description,
                        ))
                        if html:
                            item = parse_html_article(html, article_url, source)
                            if item:
                                all_items.append(item)

                elif source.source_type == "html":
                    # Listagem HTML: extrai URLs de artigos, busca cada um
                    article_urls = parse_html_listing(content, source)
                    for article_url in article_urls[:limit_per_source]:
                        html = await self._fetch(client, Source(
                            slug=source.slug,
                            name=source.name,
                            source_type="html",
                            url=article_url,
                            domains=source.domains,
                            description=source.description,
                        ))
                        if html:
                            item = parse_html_article(html, article_url, source)
                            if item:
                                all_items.append(item)

        # Ordena por data (mais recente primeiro), depois por fonte
        all_items.sort(key=lambda x: x["date"] or "", reverse=True)
        return all_items

    def crawl_sync(
        self,
        sources: List[Source],
        limit_per_source: int = 15,
    ) -> List[dict]:
        """Wrapper síncrono. Processa fontes browser (Playwright) fora do asyncio,
        depois chama o crawl assíncrono para RSS/API/HTML/sitemap."""
        all_items = []

        # Browser sources: Playwright não roda dentro de asyncio.run()
        browser_sources = [s for s in sources if s.source_type == "browser"]
        http_sources = [s for s in sources if s.source_type != "browser"]

        for source in browser_sources:
            try:
                items = parse_browser(source.url, source, limit_per_source)
                all_items.extend(items)
            except Exception:
                pass

        if http_sources:
            async_items = asyncio.run(self.crawl(http_sources, limit_per_source))
            all_items.extend(async_items)

        all_items.sort(key=lambda x: x["date"] or "", reverse=True)
        return all_items
