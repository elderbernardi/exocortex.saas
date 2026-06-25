#!/usr/bin/env python3
"""CLI do coletor de CNPJ."""

from __future__ import annotations

import argparse
import json
import sys

from .collector import CNPJCollector


def render_text(result: dict) -> str:
    data = result["data"]
    lines = [
        f"CNPJ: {data.get('cnpj') or '-'}",
        f"Razão social: {data.get('razao_social') or '-'}",
        f"Nome fantasia: {data.get('nome_fantasia') or '-'}",
        f"Situação cadastral: {data.get('situacao_cadastral') or '-'}",
        f"Data de abertura: {data.get('data_abertura') or '-'}",
        f"Capital social: {data.get('capital_social') if data.get('capital_social') is not None else '-'}",
        f"CNAEs: {len(data.get('cnaes') or [])}",
        f"Sócios: {len(data.get('socios') or [])}",
        f"Filiais: {len(data.get('filiais') or [])}",
        f"Fonte: {result['provenance'].get('url') or '-'}",
    ]
    if result.get("errors"):
        lines.append("Erros:")
        for error in result["errors"]:
            lines.append(f"- [{error.get('source') or 'collector'}] {error.get('code')}: {error.get('message')}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="excrtx-source-cnpj",
        description="Consulta dados cadastrais de CNPJ em APIs públicas brasileiras.",
    )
    parser.add_argument("cnpj", help="CNPJ com 14 dígitos (máscara opcional)")
    parser.add_argument(
        "--output",
        "-o",
        choices=["json", "text"],
        default="json",
        help="Formato de saída (default: json)",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Ignora cache local e força consulta nas APIs",
    )
    args = parser.parse_args()

    collector = CNPJCollector(use_cache=not args.no_cache)
    result = collector.lookup(args.cnpj)

    if args.output == "json":
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(render_text(result))

    sys.exit(0 if not result.get("errors") else 1)


if __name__ == "__main__":
    main()
