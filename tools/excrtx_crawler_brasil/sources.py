"""
Fontes brasileiras setoriais para o crawler.

Cada fonte é registrada com: nome, tipo (rss/api/html), URL, domínio(s) e parser.
Fontes zero-config: sem autenticação, sem paywall, sem cookies.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Source:
    """Uma fonte de coleta setorial brasileira."""

    slug: str               # identificador único (ex: "valor-economico")
    name: str               # nome exibível (ex: "Valor Econômico")
    source_type: str        # "rss", "api", "html"
    url: str                # URL do feed, API endpoint ou página
    domains: List[str]      # domínios cobertos (ex: ["economia", "negocios"])
    description: str        # descrição da fonte
    language: str = "pt-BR"

    # Metadados de coleta
    rate_limit_seconds: float = 2.0   # intervalo mínimo entre requests
    cache_ttl_minutes: int = 15       # TTL do cache
    timeout_seconds: float = 30.0     # timeout do request


# ── CPG / FMCG — Fontes de negócios e economia ──────────────────────────────

CPG_SOURCES: List[Source] = [
    Source(
        slug="valor-economico",
        name="Valor Econômico",
        source_type="rss",
        url="https://pox.globo.com/rss/valor",
        domains=["cpg", "economia", "negocios", "financas"],
        description="Principal veículo de economia, finanças e negócios do Brasil",
    ),
    Source(
        slug="exame",
        name="Exame",
        source_type="rss",
        url="https://exame.com/feed/",
        domains=["cpg", "economia", "negocios"],
        description="Revista de negócios, economia e finanças",
    ),
    Source(
        slug="g1-economia",
        name="G1 Economia",
        source_type="rss",
        url="https://g1.globo.com/rss/g1/economia/",
        domains=["cpg", "economia", "governo"],
        description="Notícias de economia do portal G1",
    ),
    Source(
        slug="infomoney",
        name="InfoMoney",
        source_type="rss",
        url="https://www.infomoney.com.br/feed/",
        domains=["cpg", "financas", "economia", "investimentos"],
        description="Portal de finanças, economia e investimentos",
    ),
    Source(
        slug="brazil-journal",
        name="Brazil Journal",
        source_type="rss",
        url="https://braziljournal.com/feed/",
        domains=["cpg", "negocios", "economia"],
        description="Jornal digital de negócios e economia",
    ),
    Source(
        slug="cnn-brasil",
        name="CNN Brasil",
        source_type="rss",
        url="https://www.cnnbrasil.com.br/feed/",
        domains=["cpg", "geral", "economia"],
        description="Notícias gerais com seção de economia",
    ),
    Source(
        slug="agencia-brasil",
        name="Agência Brasil",
        source_type="rss",
        url="https://agenciabrasil.ebc.com.br/rss/ultimasnoticias/feed.xml",
        domains=["governo", "geral"],
        description="Agência de notícias oficial do governo federal",
    ),
    Source(
        slug="google-news-economia",
        name="Google News Brasil — Economia",
        source_type="rss",
        url="https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB?hl=pt-BR&gl=BR&ceid=BR:pt-419",
        domains=["cpg", "economia", "geral"],
        description="Agregador de notícias de economia do Google News Brasil",
    ),
    Source(
        slug="food-connection",
        name="Food Connection",
        source_type="rss",
        url="https://www.foodconnection.com.br/feed/",
        domains=["alimentos", "cpg"],
        description="Portal especializado em indústria de alimentos e bebidas",
    ),
    Source(
        slug="embalagem-marca",
        name="Embalagem & Marca",
        source_type="rss",
        url="https://embalagemmarca.com.br/feed/",
        domains=["embalagens", "cpg"],
        description="Portal do setor de embalagens e bens de consumo",
    ),
    Source(
        slug="superhiper",
        name="SuperHiper (ABRAS)",
        source_type="rss",
        url="https://www.superhiper.com.br/feed/",
        domains=["varejo", "cpg", "supermercados"],
        description="Revista da ABRAS — Associação Brasileira de Supermercados",
    ),
    Source(
        slug="household-innovation",
        name="Household Innovation",
        source_type="rss",
        url="https://householdinnovation.com.br/feed/",
        domains=["cpg", "limpeza", "domesticos"],
        description="Portal de inovação em produtos de limpeza e household",
    ),
    Source(
        slug="scanntech",
        name="Scanntech",
        source_type="html",
        url="https://www.scanntech.com.br/noticias/",
        domains=["varejo", "cpg", "tecnologia"],
        description="Informações e rankings do varejo alimentar brasileiro",
        rate_limit_seconds=3.0,
    ),
    Source(
        slug="nielsen",
        name="Nielsen Insights",
        source_type="api",
        url="https://www.nielsen.com/wp-json/wp/v2/insight?per_page=10",
        domains=["cpg", "varejo", "consumidor", "insights"],
        description="Insights de mercado e comportamento do consumidor — Nielsen (global, com conteúdo PT-BR)",
        rate_limit_seconds=3.0,
    ),
    Source(
        slug="supervarejo",
        name="SuperVarejo",
        source_type="browser",
        url="https://supervarejo.com.br/noticias/",
        domains=["varejo", "cpg", "supermercados"],
        description="Portal de notícias do varejo — ABRAS/SuperVarejo (renderização JS)",
        rate_limit_seconds=5.0,
        timeout_seconds=45.0,
    ),
]


def get_sources(domains: Optional[List[str]] = None) -> List[Source]:
    """Retorna fontes filtradas por domínio(s). Domínios: economia, negocios, financas,
    alimentos, cpg, embalagens, governo, geral.
    Se domains for None, retorna todas."""
    if domains is None:
        return list(CPG_SOURCES)

    domain_set = set(d.lower() for d in domains)
    return [s for s in CPG_SOURCES if domain_set & set(d.lower() for d in s.domains)]


def get_source(slug: str) -> Optional[Source]:
    """Retorna uma fonte pelo slug."""
    for s in CPG_SOURCES:
        if s.slug == slug:
            return s
    return None
