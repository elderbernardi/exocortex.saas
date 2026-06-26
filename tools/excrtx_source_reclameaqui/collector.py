"""Coletor de reputação pública no Reclame Aqui via HTTP/HTML.

Estratégia de coleta:
1. Monta a URL canônica: https://www.reclameaqui.com.br/empresa/{slug}/
2. Faz GET com httpx, tratando Cloudflare, rate limit e erros de forma estruturada.
3. Se receber HTML válido (sem Cloudflare challenge), faz parse com BeautifulSoup.
4. Se encontrar JSON embutido (Next.js __NEXT_DATA__), extrai dados desse JSON.

NOTA: Em 2026, o Reclame Aqui usa Cloudflare Turnstile/managed challenge em todas
as rotas. O acesso por HTTP puro ou headless sem resistor de challenge é bloqueado
com HTTP 403 e página "Just a moment...". Este coletor reporta esse bloqueio de
forma estruturada no envelope, sem inventar dados.

Futuros caminhos:
- Firecrawl MCP (se configurado) pode resolver o challenge.
- Browser agent com Playwright pode resolver challenges interativos.
- APIs não-oficiais (iosearch) também estão atrás do Cloudflare.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any

import httpx
from bs4 import BeautifulSoup, Tag

from .schemas import (
    empty_data,
    make_envelope,
    make_error,
    now_utc,
    parse_float,
    parse_int,
    parse_percentage,
    slugify_query,
)

BASE_URL = "https://www.reclameaqui.com.br/empresa/{slug}/"
USER_AGENT = "exocortex-reclameaqui-collector/1.0"
CLOUDFLARE_TITLE_PATTERNS = ("just a moment", "performing security verification")
CLOUDFLARE_STATUS_CODES = {403, 503}


class ReclameAquiCollector:
    def __init__(
        self,
        *,
        timeout_seconds: float = 20.0,
        transport: httpx.BaseTransport | None = None,
    ):
        self.timeout_seconds = timeout_seconds
        self.transport = transport
        self._last_request_at: float = 0.0

    def lookup(self, query: str) -> dict:
        """Look up a company on Reclame Aqui.

        Args:
            query: Company name, slug, or full Reclame Aqui URL.
        """
        slug = slugify_query(query)
        if not slug:
            return make_envelope(
                query,
                empty_data(),
                provenance_url="",
                errors=[make_error("invalid_query", "Query não produz slug válido", "validation")],
            )

        url = BASE_URL.format(slug=slug)
        self._respect_rate_limit()

        html_body, errors = self._fetch_html(url)
        if errors:
            return make_envelope(
                query,
                empty_data(),
                provenance_url=url,
                method="html",
                errors=errors,
            )

        # Detect Cloudflare challenge page
        if self._is_cloudflare_challenge(html_body):
            return make_envelope(
                query,
                empty_data(),
                provenance_url=url,
                method="html",
                errors=[
                    make_error(
                        "cloudflare_challenge",
                        "Reclame Aqui requer verificação Cloudflare (Turnstile/managed challenge). "
                        "Acesso por HTTP puro ou browser headless sem resistor de challenge é bloqueado. "
                        "Caminhos futuros: Firecrawl MCP, browser agent com Playwright, ou API com token.",
                        "cloudflare",
                    )
                ],
            )

        # At this point html_body is guaranteed non-None
        assert html_body is not None

        # Try Next.js embedded JSON first
        next_data = self._extract_next_data(html_body)
        if next_data:
            data = self._parse_next_data(next_data, slug)
            meaningful = any(
                [
                    data.get("nota_geral") is not None,
                    data.get("total_reclamacoes") is not None,
                    data.get("respondidas") is not None,
                    data.get("taxa_resolucao") is not None,
                    bool(data.get("categorias_problema")),
                    bool(data.get("reclamacoes")),
                ]
            )
            if meaningful:
                return make_envelope(query, data, provenance_url=url, method="html")

        # Fallback to HTML scraping
        data = self._parse_html(html_body, slug)
        return make_envelope(query, data, provenance_url=url, method="html")

    def _fetch_html(self, url: str) -> tuple[str | None, list[dict]]:
        """Fetch HTML from the given URL. Returns (html_or_None, errors)."""
        try:
            with httpx.Client(
                timeout=self.timeout_seconds,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                },
                transport=self.transport,
                follow_redirects=True,
            ) as client:
                response = client.get(url)
        except httpx.TimeoutException:
            return None, [make_error("timeout", "Timeout ao consultar Reclame Aqui", "network")]
        except httpx.HTTPError as exc:
            return None, [make_error("network_error", str(exc), "network")]

        if response.status_code in CLOUDFLARE_STATUS_CODES:
            # Check if body is a Cloudflare challenge page
            body = response.text
            if self._is_cloudflare_challenge(body):
                return body, []  # Return body so caller can report structured error

            return None, [
                make_error(
                    "http_error",
                    f"HTTP {response.status_code} — possível bloqueio Cloudflare",
                    "http",
                )
            ]

        if response.status_code == 404:
            return None, [make_error("not_found", "Empresa não encontrada no Reclame Aqui", "http")]
        if response.status_code == 429:
            return None, [make_error("rate_limited", "Rate limit no Reclame Aqui", "http")]
        if response.status_code >= 400:
            return None, [
                make_error("http_error", f"HTTP {response.status_code}", "http")
            ]

        return response.text, []

    @staticmethod
    def _is_cloudflare_challenge(html: str | None) -> bool:
        """Check if the HTML body is a Cloudflare challenge page."""
        if not html:
            return False
        title_match = re.search(r"<title>([^<]+)</title>", html, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip().lower()
            for pattern in CLOUDFLARE_TITLE_PATTERNS:
                if pattern in title:
                    return True
        # Also check for Cloudflare challenge markers in the body
        if "challenges.cloudflare.com" in html or "__cf_chl_rt_tk" in html:
            return True
        return False

    @staticmethod
    def _extract_next_data(html: str) -> dict | None:
        """Extract JSON from Next.js __NEXT_DATA__ script tag."""
        match = re.search(
            r'<script\s+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
            html,
            re.DOTALL,
        )
        if not match:
            return None
        try:
            return json.loads(match.group(1))
        except (json.JSONDecodeError, ValueError):
            return None

    def _parse_next_data(self, next_data: dict, slug: str) -> dict:
        """Parse data from Next.js __NEXT_DATA__ structure."""
        try:
            # Navigate the Next.js data structure
            props = next_data.get("props", {}).get("pageProps", {})
            # The exact structure depends on RA's page structure; try common patterns
            company = props.get("company") or props.get("empresa") or {}
            complaints_data = props.get("complaints") or props.get("reclamacoes") or {}

            data = empty_data()
            data["slug"] = slug
            data["empresa"] = (
                company.get("name")
                or company.get("nome")
                or company.get("razaoSocial")
                or company.get("title")
                or slug.replace("-", " ").title()
            )
            data["nota_geral"] = parse_float(
                company.get("score") or company.get("nota") or company.get("rating")
            )
            data["total_reclamacoes"] = parse_int(
                company.get("totalComplaints")
                or company.get("total_complaints")
                or company.get("totalReclamacoes")
            )
            data["respondidas"] = parse_int(
                company.get("answered")
                or company.get("respondidas")
                or company.get("totalAnswered")
            )
            data["taxa_resolucao"] = parse_percentage(
                company.get("solutionRate")
                or company.get("taxaResolucao")
                or company.get("resolution_rate")
            )

            # Parse complaint list if available
            complaints_list = complaints_data.get("list") or complaints_data.get("items") or []
            parsed_complaints = []
            for c in complaints_list[:20]:
                parsed_complaints.append(
                    {
                        "titulo": c.get("title") or c.get("titulo") or None,
                        "data": c.get("created") or c.get("data") or c.get("date") or None,
                        "status": c.get("status") or None,
                        "categoria": c.get("category") or c.get("categoria") or None,
                    }
                )
            data["reclamacoes"] = parsed_complaints

            # Parse categories
            categories = company.get("categories") or company.get("categoriasProblema") or []
            parsed_categories = []
            for cat in categories:
                parsed_categories.append(
                    {
                        "categoria": cat.get("name") or cat.get("nome") or cat.get("category") or str(cat),
                        "count": parse_int(cat.get("count") or cat.get("total") or cat.get("quantity")),
                    }
                )
            data["categorias_problema"] = parsed_categories

            return data
        except Exception:
            return empty_data()

    def _parse_html(self, html: str, slug: str) -> dict:
        """Parse company data from traditional HTML markup."""
        soup = BeautifulSoup(html, "html.parser")
        data = empty_data()
        data["slug"] = slug

        # Company name
        name_el = (
            soup.select_one("h1")
            or soup.select_one("[data-testid='company-name']")
            or soup.select_one(".company-name")
            or soup.select_one(".title-company")
        )
        if name_el:
            data["empresa"] = name_el.get_text(strip=True)

        # JSON-LD / meta description são a fonte mais estável da página.
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            raw = script.get_text(strip=True)
            if not raw:
                continue
            try:
                payload = json.loads(raw)
            except (json.JSONDecodeError, ValueError, TypeError):
                continue
            items = payload if isinstance(payload, list) else [payload]
            for item in items:
                if not isinstance(item, dict):
                    continue
                if not data["empresa"]:
                    data["empresa"] = item.get("name") or item.get("legalName") or data["empresa"]
                agg = item.get("aggregateRating")
                if isinstance(agg, list):
                    agg = agg[0] if agg else None
                if isinstance(agg, dict):
                    data["nota_geral"] = data["nota_geral"] or parse_float(agg.get("ratingValue"))
                    data["total_reclamacoes"] = data["total_reclamacoes"] or parse_int(agg.get("ratingCount"))

        meta_description = ""
        meta_el = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        if meta_el and meta_el.get("content"):
            meta_description = str(meta_el.get("content") or "")
            nota_match = re.search(r"Nota\s+([\d,.]+)\s*/\s*10", meta_description, re.IGNORECASE)
            complaints_match = re.search(r"recebeu\s+(\d+)\s+reclama", meta_description, re.IGNORECASE)
            if nota_match and data["nota_geral"] is None:
                data["nota_geral"] = parse_float(nota_match.group(1))
            if complaints_match and data["total_reclamacoes"] is None:
                data["total_reclamacoes"] = parse_int(complaints_match.group(1))

        # Overall score
        score_el = (
            soup.select_one("[data-testid='score-value']")
            or soup.select_one(".score-value")
            or soup.select_one(".ra-score")
            or soup.select_one("[class*='score']")
        )
        if score_el and data["nota_geral"] is None:
            data["nota_geral"] = parse_float(score_el.get_text(strip=True))

        # Total complaints
        if data["total_reclamacoes"] is None:
            for el in soup.select("[class*='complaint'], [class*='reclamacao']"):
                text = el.get_text(strip=True)
                num = parse_int(text)
                if num is not None and num > 0:
                    data["total_reclamacoes"] = num
                    break

        response_pct = None
        resolution_match = re.search(r"resolveu\s*<strong[^>]*>\s*([\d.,]+)%\s+das reclamações", html, re.IGNORECASE)
        if resolution_match:
            data["taxa_resolucao"] = parse_percentage(resolution_match.group(1))

        response_match = re.search(r"Respondeu\s*<strong[^>]*>\s*([\d.,]+)%\s+das reclamações", html, re.IGNORECASE)
        if response_match:
            response_pct = parse_percentage(response_match.group(1))
        if response_pct is not None and data["total_reclamacoes"] is not None:
            data["respondidas"] = int(round(data["total_reclamacoes"] * response_pct))

        avg_time_match = re.search(r"tempo médio de resposta é\s*<strong[^>]*>\s*([^<]+)", html, re.IGNORECASE)
        if avg_time_match:
            data["tempo_medio_resposta"] = avg_time_match.group(1).strip()

        # Individual complaints
        complaints = []
        for el in soup.select("[class*='complaint-card'], [class*='complaint-card-wrapper'], article"):
            title_el = el.select_one("h2, h3, [class*='title'], [class*='titulo']")
            date_el = el.select_one("[class*='date'], [class*='data'], time")
            status_el = el.select_one("[class*='status']")
            category_el = el.select_one("[class*='category'], [class*='tag']")

            complaints.append(
                {
                    "titulo": title_el.get_text(strip=True) if title_el else None,
                    "data": date_el.get_text(strip=True) if date_el else None,
                    "status": status_el.get_text(strip=True) if status_el else None,
                    "categoria": category_el.get_text(strip=True) if category_el else None,
                }
            )
        data["reclamacoes"] = complaints[:20]

        # If we didn't find a company name, derive from slug
        if not data["empresa"]:
            data["empresa"] = slug.replace("-", " ").title()

        return data

    def _respect_rate_limit(self, min_interval: float = 2.0) -> None:
        now = time.time()
        delta = now - self._last_request_at
        if delta < min_interval:
            time.sleep(min_interval - delta)
        self._last_request_at = time.time()
