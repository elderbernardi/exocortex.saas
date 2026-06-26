#!/usr/bin/env python3
"""CLI do coletor de Google Trends."""

from __future__ import annotations

import argparse
import json
import sys

from .collector import GoogleTrendsCollector


def render_text(result: dict) -> str:
    data = result["data"]
    lines = [
        f"Source: {result.get('source')}",
        f"Query: {result.get('query')}",
        f"Retrieved at: {result.get('retrieved_at')}",
    ]

    termos = data.get("termos") or []
    if termos:
        lines.append(f"Termos: {', '.join(termos)}")

    period = result.get("provenance", {}).get("period")
    if period:
        lines.append(f"Período: {period}")

    geo = result.get("provenance", {}).get("geo")
    if geo:
        lines.append(f"Região: {geo}")

    serie = data.get("serie_temporal") or {}
    for term, points in serie.items():
        values = [(p.get("date"), p.get("value")) for p in points if p.get("value") is not None]
        if values:
            max_v = max(values, key=lambda x: x[1] or 0)
            min_v = min(values, key=lambda x: x[1] or 0)
            lines.append(f"  {term}: {len(points)} pontos (máx {max_v[1]} em {max_v[0]}; mín {min_v[1]} em {min_v[0]})")
        else:
            lines.append(f"  {term}: sem dados temporais")

    regioes = data.get("interesse_por_regiao") or {}
    for term, geo_data in regioes.items():
        if geo_data:
            top = sorted(geo_data.items(), key=lambda x: x[1] or 0, reverse=True)[:5]
            top_str = ", ".join(f"{k}: {v}" for k, v in top)
            lines.append(f"  Região [{term}]: {top_str}")

    queries = data.get("queries_relacionadas") or {}
    for term, qq in queries.items():
        if qq.get("rising"):
            lines.append(f"  Rising [{term}]: {', '.join(qq['rising'][:5])}")
        if qq.get("top"):
            lines.append(f"  Top [{term}]: {', '.join(qq['top'][:5])}")

    suggestions = data.get("autocomplete_suggestions") or []
    if suggestions:
        lines.append(f"  Autocomplete: {', '.join(suggestions)}")

    if result.get("errors"):
        lines.append("Erros:")
        for error in result["errors"]:
            lines.append(f"- [{error.get('source') or 'collector'}] {error.get('code')}: {error.get('message')}")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="excrtx-source-google-trends",
        description="Consulta Google Trends via API pública (endpoint explore).",
    )
    parser.add_argument("query", help="Termo(s) de busca, separados por vírgula")
    parser.add_argument(
        "--period",
        "-p",
        default="today 5-Y",
        help="Período (ex.: '7d', '1m', '3m', '12m', '5y', ou 'YYYY-MM-DD YYYY-MM-DD')",
    )
    parser.add_argument(
        "--geo",
        "-g",
        default="BR",
        help="Código de região (ex.: BR, US, CL)",
    )
    parser.add_argument(
        "--category",
        "-c",
        type=int,
        default=0,
        help="Categoria Google Trends (0=todas)",
    )
    parser.add_argument(
        "--output",
        "-o",
        choices=["json", "text"],
        default="json",
        help="Formato de saída (default: json)",
    )
    parser.add_argument(
        "--autocomplete",
        "-a",
        action="store_true",
        help="Inclui sugestões de autocomplete do termo",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        help="Timeout em segundos",
    )
    args = parser.parse_args()

    collector = GoogleTrendsCollector(timeout_seconds=args.timeout)
    result = collector.lookup(
        args.query,
        period=args.period,
        geo=args.geo,
        category=args.category,
        include_related=True,
        include_autocomplete=args.autocomplete,
    )

    if args.output == "json":
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(render_text(result))

    sys.exit(0 if not result.get("errors") else 1)


if __name__ == "__main__":
    main()
