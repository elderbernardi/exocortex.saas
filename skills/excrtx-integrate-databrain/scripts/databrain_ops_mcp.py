#!/usr/bin/env python3
"""MCP stdio do plano de controle DataBrain para o Exocórtex."""

from __future__ import annotations

import argparse
import asyncio
import json
from typing import Any

from fastmcp import FastMCP

from databrain_ops_core import (
    capabilities,
    get_run,
    health,
    list_inbox,
    list_runs,
    operation_logs,
    operation_status,
    prepare_operation,
    start_operation,
)

SERVER_NAME = "databrain-ops"
SERVER_INSTRUCTIONS = (
    "Governed operational control plane for Projeto B DataBrain. "
    "Only named operations are allowed; arbitrary shell is impossible. "
    "External publish operations require a post-DRAFT approval_ref."
)


def ok(message: str, **payload: Any) -> dict[str, Any]:
    return {"status": "ok", "message": message, **payload}


def error(exc: Exception, **payload: Any) -> dict[str, Any]:
    return {"status": "error", "message": str(exc), **payload}


def create_server() -> FastMCP:
    app = FastMCP(SERVER_NAME, instructions=SERVER_INSTRUCTIONS)

    @app.tool(name="databrain_capabilities")
    def databrain_capabilities() -> dict[str, Any]:
        """Lista operações permitidas, efeitos e gates de aprovação."""
        return ok("capacidades listadas", **capabilities())

    @app.tool(name="databrain_health")
    def databrain_health() -> dict[str, Any]:
        """Saúde da API, container e último pipeline do DataBrain ativo."""
        try:
            return health()
        except Exception as exc:
            return error(exc)

    @app.tool(name="databrain_list_runs")
    def databrain_list_runs(limit: int = 10, status: str | None = None) -> dict[str, Any]:
        """Lista execuções recentes do pipeline pelo Cockpit API local."""
        try:
            return list_runs(limit=limit, status=status)
        except Exception as exc:
            return error(exc)

    @app.tool(name="databrain_get_run")
    def databrain_get_run(run_id: str) -> dict[str, Any]:
        """Retorna detalhes de uma pipeline_run específica."""
        try:
            return get_run(run_id)
        except Exception as exc:
            return error(exc, run_id=run_id)

    @app.tool(name="databrain_list_inbox")
    def databrain_list_inbox(limit: int = 50) -> dict[str, Any]:
        """Lista arquivos aguardando ingestão na inbox de produção, sem ler conteúdo."""
        try:
            return list_inbox(limit=limit)
        except Exception as exc:
            return error(exc)

    @app.tool(name="databrain_prepare_operation")
    def databrain_prepare_operation(operation: str, requested_by: str = "exocortex") -> dict[str, Any]:
        """Prepara receipt imutável para uma operação nomeada; não executa nada."""
        try:
            receipt = prepare_operation(operation=operation, requested_by=requested_by)
            return ok("operação preparada", receipt=receipt)
        except Exception as exc:
            return error(exc, operation=operation)

    @app.tool(name="databrain_start_operation")
    def databrain_start_operation(receipt_id: str, approval_ref: str | None = None) -> dict[str, Any]:
        """Inicia operação preparada. Publicações exigem approval_ref pós-DRAFT."""
        try:
            operation = start_operation(receipt_id=receipt_id, approval_ref=approval_ref)
            return ok("operação iniciada", operation=operation)
        except Exception as exc:
            return error(exc, receipt_id=receipt_id)

    @app.tool(name="databrain_operation_status")
    def databrain_operation_status(operation_id: str) -> dict[str, Any]:
        """Consulta estado e código de saída de uma operação iniciada pela ponte."""
        try:
            return operation_status(operation_id)
        except Exception as exc:
            return error(exc, operation_id=operation_id)

    @app.tool(name="databrain_operation_logs")
    def databrain_operation_logs(operation_id: str, tail_lines: int = 200) -> dict[str, Any]:
        """Retorna cauda do log auditável da operação, limitada a 1000 linhas."""
        try:
            return operation_logs(operation_id, tail_lines=tail_lines)
        except Exception as exc:
            return error(exc, operation_id=operation_id)

    return app


def self_test() -> dict[str, Any]:
    server = create_server()

    async def run() -> dict[str, Any]:
        tools = sorted(tool.name for tool in await server.list_tools())
        result: dict[str, Any] = {
            "ok": len(tools) == 9,
            "server": SERVER_NAME,
            "tool_count": len(tools),
            "tools": tools,
            "capabilities": capabilities(),
        }
        try:
            result["health"] = health()
            result["ok"] = result["ok"] and result["health"]["api"].get("status") == "ok"
        except Exception as exc:
            result["health_error"] = str(exc)
            result["ok"] = False
        return result

    return asyncio.run(run())


def main() -> int:
    parser = argparse.ArgumentParser(description="DataBrain Ops MCP")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        result = self_test()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get("ok") else 1
    create_server().run(transport="stdio", show_banner=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
