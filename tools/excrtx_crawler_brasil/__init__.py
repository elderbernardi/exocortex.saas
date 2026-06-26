"""excrtx-crawler-brasil — Coleta em fontes setoriais brasileiras."""

from .crawler import CrawlerBrasil
from .sources import CPG_SOURCES, get_sources, get_source, Source

__version__ = "1.0.0"
__all__ = ["CrawlerBrasil", "CPG_SOURCES", "get_sources", "get_source", "Source"]
