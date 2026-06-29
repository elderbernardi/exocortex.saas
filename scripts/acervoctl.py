#!/usr/bin/env python3
"""CLI operacional do Acervo Control Plane.

Superfície local oficial para provar o contrato prepare/commit antes da camada MCP.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from acervo_semantic_core import (
    commit_write,
    export_microverso,
    list_microversos,
    prepare_write,
    search_acervo,
    slugify,
    validate_entry,
)


def print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def write_receipt_if_needed(payload: dict[str, Any], receipt_out: str | None) -> None:
    if not receipt_out:
        return
    Path(receipt_out).expanduser().write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_receipt(raw: str) -> dict[str, Any]:
    candidate = Path(raw).expanduser()
    if candidate.exists():
        return json.loads(candidate.read_text(encoding="utf-8"))
    return json.loads(raw)


def command_list_microversos(args: argparse.Namespace) -> dict[str, Any]:
    microversos = list_microversos(args.acervo_root)
    return {"ok": True, "microversos": microversos, "count": len(microversos)}


def command_search(args: argparse.Namespace) -> dict[str, Any]:
    matches = search_acervo(args.acervo_root, args.query, limit=args.limit)
    return {"ok": True, "query": args.query, "count": len(matches), "matches": matches}


def command_prepare_write(args: argparse.Namespace) -> dict[str, Any]:
    filename = args.filename or f"{slugify(args.title)}.md"
    payload = prepare_write(
        acervo_root=args.acervo_root,
        microverso=args.microverso,
        nature=args.nature,
        filename=filename,
        active_microverso=args.active_microverso or args.microverso,
    )
    write_receipt_if_needed(payload, args.receipt_out)
    return payload


def command_commit_write(args: argparse.Namespace) -> dict[str, Any]:
    prepared = load_receipt(args.receipt)
    if args.content_file:
        content = Path(args.content_file).expanduser().read_text(encoding="utf-8")
    elif args.content is not None:
        content = args.content
    else:
        raise RuntimeError("Informe --content-file ou --content para commit-write.")

    return commit_write(
        prepared,
        content=content,
        entry_type=args.entry_type,
        description=args.description,
        class_name=args.class_name,
    )


def command_validate_frontmatter(args: argparse.Namespace) -> dict[str, Any]:
    validate_entry(args.path)
    return {"ok": True, "path": str(Path(args.path).expanduser().resolve())}


def command_export_microverso(args: argparse.Namespace) -> dict[str, Any]:
    return export_microverso(
        acervo_root=args.acervo_root,
        slug=args.slug,
        out_dir=args.out,
        tar=args.tar,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Acervo Control Plane CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    list_cmd = sub.add_parser("list-microversos", help="Lista microversos disponíveis")
    list_cmd.add_argument("--acervo-root", help="Raiz do Acervo")
    list_cmd.set_defaults(handler=command_list_microversos)

    search_cmd = sub.add_parser("search", help="Busca simples em markdown do Acervo")
    search_cmd.add_argument("--acervo-root", help="Raiz do Acervo")
    search_cmd.add_argument("--query", required=True)
    search_cmd.add_argument("--limit", type=int, default=20)
    search_cmd.set_defaults(handler=command_search)

    prepare_cmd = sub.add_parser("prepare-write", help="Prepara uma mutação semântica")
    prepare_cmd.add_argument("--acervo-root", help="Raiz do Acervo")
    prepare_cmd.add_argument("--microverso", required=True)
    prepare_cmd.add_argument("--nature", required=True)
    prepare_cmd.add_argument("--title", required=True)
    prepare_cmd.add_argument("--filename", help="Override explícito do nome do arquivo")
    prepare_cmd.add_argument("--active-microverso", help="Override do microverso ativo")
    prepare_cmd.add_argument("--receipt-out", help="Arquivo para gravar o receipt JSON")
    prepare_cmd.set_defaults(handler=command_prepare_write)

    commit_cmd = sub.add_parser("commit-write", help="Efetiva uma mutação semântica preparada")
    commit_cmd.add_argument("--receipt", required=True, help="JSON inline ou caminho para receipt")
    commit_cmd.add_argument("--content-file", help="Arquivo markdown a gravar")
    commit_cmd.add_argument("--content", help="Conteúdo inline markdown")
    commit_cmd.add_argument("--entry-type", default="CREATED")
    commit_cmd.add_argument("--description", required=True)
    commit_cmd.add_argument("--class-name", default="volátil")
    commit_cmd.set_defaults(handler=command_commit_write)

    validate_cmd = sub.add_parser("validate-frontmatter", help="Valida frontmatter de um arquivo")
    validate_cmd.add_argument("--path", required=True)
    validate_cmd.set_defaults(handler=command_validate_frontmatter)

    export_cmd = sub.add_parser("export-microverso", help="Empacota um microverso")
    export_cmd.add_argument("--acervo-root", help="Raiz do Acervo")
    export_cmd.add_argument("--slug", required=True)
    export_cmd.add_argument("--out", required=True)
    export_cmd.add_argument("--tar", action="store_true")
    export_cmd.set_defaults(handler=command_export_microverso)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        payload = args.handler(args)
    except Exception as exc:
        print_json({"ok": False, "error": str(exc)})
        return 1
    print_json(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
