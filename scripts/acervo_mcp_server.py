#!/usr/bin/env python3
"""Servidor MCP fino do Acervo Control Plane.

Objetivo: expor o core semântico via MCP stdio sem duplicar regra local.
As tools aqui só adaptam entrada/saída e delegam para o core / runtime guard.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

import yaml
from fastmcp import FastMCP

from acervo_semantic_core import (
    commit_write,
    export_microverso,
    list_microversos,
    prepare_write,
    relative_to_acervo,
    resolve_acervo_root,
    search_acervo,
    slugify,
    validate_entry,
)
from exocortex_runtime_guard import guard_write_path

SERVER_NAME = "acervo"
SERVER_INSTRUCTIONS = (
    "Semantic control plane for Acervo microverses. "
    "Filesystem remains the physical source of truth; semantic agentic writes "
    "must flow through prepare/commit or the higher-level create/update tools."
)


def _ok(message: str, **payload: Any) -> dict[str, Any]:
    data = {"status": "ok", "message": message, "warnings": payload.pop("warnings", [])}
    data.update(payload)
    return data



def _error(message: str, **payload: Any) -> dict[str, Any]:
    data = {"status": "error", "message": message, "warnings": payload.pop("warnings", [])}
    data.update(payload)
    return data



def _resolve_page_path(acervo_root: str | Path | None, path: str) -> tuple[Path, Path]:
    root = resolve_acervo_root(acervo_root)
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = (root / candidate).resolve()
    else:
        candidate = candidate.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise RuntimeError(f"Path fora do Acervo: {candidate}") from exc
    if candidate.suffix != ".md":
        raise RuntimeError(f"Leitura semântica suporta apenas .md neste corte: {candidate}")
    if not candidate.exists():
        raise RuntimeError(f"Página inexistente: {candidate}")
    return root, candidate



def _normalize_receipt(receipt: dict[str, Any] | str) -> dict[str, Any]:
    if isinstance(receipt, dict):
        return receipt
    try:
        return json.loads(receipt)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Receipt inválido: esperado dict ou JSON válido.") from exc



def _render_entry_markdown(
    *,
    title: str,
    body: str,
    nature: str,
    entry_type: str,
    description: str,
    tags: list[str] | None,
    class_name: str,
    timestamp: str,
    created_at: str,
    created: str,
    updated: str,
    excrtx_type: str,
    confidence: str,
    sources: list[str] | None,
) -> str:
    frontmatter = {
        "type": entry_type,
        "title": title,
        "description": description,
        "tags": tags or [],
        "timestamp": timestamp,
        "class": class_name,
        "created_at": created_at,
        "created": created,
        "updated": updated,
        "nature": nature,
        "excrtx_type": excrtx_type,
        "confidence": confidence,
        "sources": sources or [],
    }
    return (
        "---\n"
        + yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
        + "\n---\n\n"
        + f"# {title}\n\n{body.strip()}\n"
    )



def create_server() -> FastMCP:
    app = FastMCP(SERVER_NAME, instructions=SERVER_INSTRUCTIONS)

    @app.tool(name="acervo_list_microversos")
    def acervo_list_microversos(acervo_root: str | None = None) -> dict[str, Any]:
        microversos = list_microversos(acervo_root)
        return _ok("microversos listados", microversos=microversos, count=len(microversos))

    @app.tool(name="acervo_search")
    def acervo_search(query: str, acervo_root: str | None = None, limit: int = 20) -> dict[str, Any]:
        matches = search_acervo(acervo_root, query, limit=limit)
        return _ok("busca concluída", query=query, count=len(matches), matches=matches)

    @app.tool(name="acervo_read_page")
    def acervo_read_page(path: str, acervo_root: str | None = None) -> dict[str, Any]:
        try:
            root, page = _resolve_page_path(acervo_root, path)
            return _ok(
                "página carregada",
                path=str(page),
                relative_path=relative_to_acervo(page, root),
                content=page.read_text(encoding="utf-8"),
            )
        except Exception as exc:
            return _error(str(exc), path=path)

    @app.tool(name="acervo_validate_scope")
    def acervo_validate_scope(
        target_path: str,
        active_microverso: str,
        acervo_root: str | None = None,
    ) -> dict[str, Any]:
        result = guard_write_path(
            target_path=target_path,
            active_microverso=active_microverso,
            acervo_root=resolve_acervo_root(acervo_root),
        )
        if result.get("allowed"):
            return _ok("escopo permitido", result=result, path=result.get("target"))
        return _error(result.get("message", "escopo negado"), result=result, path=result.get("target"))

    @app.tool(name="acervo_validate_frontmatter")
    def acervo_validate_frontmatter(path: str) -> dict[str, Any]:
        try:
            validate_entry(path)
            return _ok("frontmatter válido", path=str(Path(path).expanduser().resolve()))
        except Exception as exc:
            return _error(str(exc), path=path)

    @app.tool(name="acervo_prepare_write")
    def acervo_prepare_write(
        microverso: str,
        nature: str,
        title: str,
        acervo_root: str | None = None,
        filename: str | None = None,
        active_microverso: str | None = None,
    ) -> dict[str, Any]:
        try:
            receipt = prepare_write(
                acervo_root=acervo_root,
                microverso=microverso,
                nature=nature,
                filename=filename or f"{slugify(title)}.md",
                active_microverso=active_microverso or microverso,
            )
            return _ok("write preparado", receipt=receipt, path=receipt["target_path"])
        except Exception as exc:
            return _error(str(exc), microverso=microverso, nature=nature, title=title)

    @app.tool(name="acervo_commit_write")
    def acervo_commit_write(
        receipt: dict[str, Any] | str,
        content: str,
        description: str,
        entry_type: str = "CREATED",
        class_name: str = "volátil",
    ) -> dict[str, Any]:
        try:
            normalized = _normalize_receipt(receipt)
            committed = commit_write(
                normalized,
                content=content,
                entry_type=entry_type,
                description=description,
                class_name=class_name,
            )
            return _ok("write efetivado", receipt=committed, path=committed["target_path"])
        except Exception as exc:
            return _error(str(exc))

    @app.tool(name="acervo_create_entry")
    def acervo_create_entry(
        microverso: str,
        nature: str,
        title: str,
        body: str,
        description: str,
        acervo_root: str | None = None,
        tags: list[str] | None = None,
        class_name: str = "volátil",
        timestamp: str = "2026-06-28",
        created_at: str = "2026-06-28T00:00:00Z",
        created: str = "2026-06-28",
        updated: str = "2026-06-28",
        entry_type: str = "knowledge",
        excrtx_type: str = "fact",
        confidence: str = "medium",
        sources: list[str] | None = None,
    ) -> dict[str, Any]:
        try:
            prepared = prepare_write(
                acervo_root=acervo_root,
                microverso=microverso,
                nature=nature,
                filename=f"{slugify(title)}.md",
                active_microverso=microverso,
            )
            content = _render_entry_markdown(
                title=title,
                body=body,
                nature=nature,
                entry_type=entry_type,
                description=description,
                tags=tags,
                class_name=class_name,
                timestamp=timestamp,
                created_at=created_at,
                created=created,
                updated=updated,
                excrtx_type=excrtx_type,
                confidence=confidence,
                sources=sources,
            )
            committed = commit_write(
                prepared,
                content=content,
                entry_type="CREATED",
                description=description,
                class_name=class_name,
            )
            return _ok("entrada criada", receipt=committed, path=committed["target_path"])
        except Exception as exc:
            return _error(str(exc), microverso=microverso, nature=nature, title=title)

    @app.tool(name="acervo_update_entry")
    def acervo_update_entry(
        microverso: str,
        nature: str,
        title: str,
        body: str,
        description: str,
        acervo_root: str | None = None,
        tags: list[str] | None = None,
        class_name: str = "volátil",
        timestamp: str = "2026-06-28",
        created_at: str = "2026-06-28T00:00:00Z",
        created: str = "2026-06-28",
        updated: str = "2026-06-28",
        entry_type: str = "knowledge",
        excrtx_type: str = "fact",
        confidence: str = "medium",
        sources: list[str] | None = None,
    ) -> dict[str, Any]:
        try:
            prepared = prepare_write(
                acervo_root=acervo_root,
                microverso=microverso,
                nature=nature,
                filename=f"{slugify(title)}.md",
                active_microverso=microverso,
            )
            content = _render_entry_markdown(
                title=title,
                body=body,
                nature=nature,
                entry_type=entry_type,
                description=description,
                tags=tags,
                class_name=class_name,
                timestamp=timestamp,
                created_at=created_at,
                created=created,
                updated=updated,
                excrtx_type=excrtx_type,
                confidence=confidence,
                sources=sources,
            )
            committed = commit_write(
                prepared,
                content=content,
                entry_type="UPDATED",
                description=description,
                class_name=class_name,
            )
            return _ok("entrada atualizada", receipt=committed, path=committed["target_path"])
        except Exception as exc:
            return _error(str(exc), microverso=microverso, nature=nature, title=title)

    @app.tool(name="acervo_export_microverso")
    def acervo_export_microverso(
        slug: str,
        out_dir: str,
        acervo_root: str | None = None,
        tar: bool = False,
    ) -> dict[str, Any]:
        try:
            exported = export_microverso(acervo_root=acervo_root, slug=slug, out_dir=out_dir, tar=tar)
            return _ok("microverso exportado", **exported)
        except Exception as exc:
            return _error(str(exc), slug=slug, out_dir=out_dir)

    return app



def run_self_test(acervo_root: str | Path | None = None) -> dict[str, Any]:
    server = create_server()

    async def _run() -> dict[str, Any]:
        tools = sorted(tool.name for tool in await server.list_tools())
        result: dict[str, Any] = {"ok": True, "server": SERVER_NAME, "tool_count": len(tools), "tools": tools}
        microversos = list_microversos(acervo_root)
        result["microversos"] = microversos
        if microversos:
            probe = await server.call_tool(
                "acervo_prepare_write",
                {
                    "acervo_root": str(resolve_acervo_root(acervo_root)),
                    "microverso": microversos[0],
                    "nature": "knowledge",
                    "title": "MCP Self Test",
                },
            )
            probe_payload = probe.structured_content or {}
            result["prepare_probe"] = probe_payload
            result["ok"] = result["ok"] and probe_payload.get("status") == "ok"
        return result

    return asyncio.run(_run())



def main() -> int:
    parser = argparse.ArgumentParser(description="Acervo MCP server")
    parser.add_argument("--self-test", action="store_true", help="Executa smoke test local sem subir o servidor")
    parser.add_argument("--acervo-root", help="Raiz do Acervo para self-test")
    args = parser.parse_args()

    if args.self_test:
        result = run_self_test(acervo_root=args.acervo_root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("ok") else 1

    server = create_server()
    server.run(transport="stdio", show_banner=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
