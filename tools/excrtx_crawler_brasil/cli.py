#!/usr/bin/env python3
"""
CLI do crawler de fontes setoriais brasileiras.

Usage:
    python3 -m tools.excrtx-crawler-brasil.cli --domain cpg --output json
    python3 -m tools.excrtx-crawler-brasil.cli --list-sources
"""

import argparse
import json
import sys

from .crawler import CrawlerBrasil
from .sources import get_sources


def main():
    parser = argparse.ArgumentParser(
        prog="excrtx-crawler-brasil",
        description="Coleta dados de fontes setoriais brasileiras",
    )
    parser.add_argument(
        "--domain", "-d",
        default="cpg",
        help="Domínio de coleta: cpg (default), economia, alimentos, geral, all",
    )
    parser.add_argument(
        "--limit", "-n",
        type=int,
        default=15,
        help="Itens máximos por fonte (default: 15)",
    )
    parser.add_argument(
        "--output", "-o",
        choices=["json", "text"],
        default="json",
        help="Formato de saída (default: json)",
    )
    parser.add_argument(
        "--sources", "-s",
        default="",
        help="Slugs de fontes separados por vírgula (default: todas do domínio)",
    )
    parser.add_argument(
        "--list-sources",
        action="store_true",
        help="Lista fontes disponíveis e sai",
    )

    args = parser.parse_args()

    # Listar fontes
    if args.list_sources:
        for s in get_sources(None):
            print(f"  {s.slug:30} [{s.source_type:3}] {s.name}")
        return

    # Selecionar fontes
    if args.domain == "all":
        sources = get_sources(None)
    else:
        sources = get_sources([args.domain])

    if args.sources:
        slugs = [x.strip() for x in args.sources.split(",")]
        sources = [s for s in sources if s.slug in slugs]

    if not sources:
        print(f"Nenhuma fonte encontrada para domínio '{args.domain}'", file=sys.stderr)
        sys.exit(1)

    # Coletar
    crawler = CrawlerBrasil()
    items = crawler.crawl_sync(sources, limit_per_source=args.limit)

    # Emitir
    if args.output == "json":
        json.dump(items, sys.stdout, ensure_ascii=False, indent=2)
    else:
        for item in items:
            print(f"[{item['source']}] {item['title']}")
            print(f"    {item['url']}")
            print(f"    {item['date']} | {item['domain']}")
            if item['snippet']:
                print(f"    {item['snippet'][:120]}...")
            print()


if __name__ == "__main__":
    main()
