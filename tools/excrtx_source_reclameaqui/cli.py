#!/usr/bin/env python3
"""CLI do coletor de Reclame Aqui."""

from __future__ import annotations

import argparse
import json
import sys

from .collector import ReclameAquiCollector


def render_text(result: dict) -> str:
    data = result["data"]
    lines = [
        f"Empresa: {data.get('empresa') or '-'}",
        f"Slug: {data.get('slug') or '-'}",
        f"Nota geral: {data.get('nota_geral') if data.get('nota_geral') is not None else '-'}",
        f"Total reclamações: {data.get('total_reclamacoes') or '-'}",
        f"Respondidas: {data.get('respondidas') or '-'}",
        f"Taxa resolução: {data.get('taxa_resolucao') if data.get('taxa_resolucao') is not None else '-'}",
        f"Categorias problema: {len(data.get('categorias_problema') or [])}",
        f"Reclamações listadas: {len(data.get('reclamacoes') or [])}",
        f"Fonte: {result['provenance'].get('url') or '-'}",
    ]
    if result.get("errors"):
        lines.append("Erros:")
        for error in result["errors"]:
            lines.append(
                f"  - [{error.get('source') or 'collector'}] "
                f"{error.get('code')}: {error.get('message')}"
            )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="excrtx-source-reclameaqui",
        description="Consulta reputação pública de empresas no Reclame Aqui.",
    )
    parser.add_argument(
        "query",
        help="Nome da empresa, slug ou URL do Reclame Aqui",
    )
    parser.add_argument(
        "--output",
        "-o",
        choices=["json", "text"],
        default="json",
        help="Formato de saída (default: json)",
    )
    args = parser.parse_args()

    collector = ReclameAquiCollector()
    result = collector.lookup(args.query)

    if args.output == "json":
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        print(render_text(result))

    sys.exit(0 if not result.get("errors") else 1)


if __name__ == "__main__":
    main()
