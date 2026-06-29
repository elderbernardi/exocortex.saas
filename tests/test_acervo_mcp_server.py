from __future__ import annotations

import asyncio
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

ENTRY_MARKDOWN = """---
type: knowledge
title: Entrada MCP
description: Criada no teste do servidor MCP
tags: [mcp, teste]
timestamp: 2026-06-28
class: volátil
created_at: 2026-06-28T00:00:00Z
created: 2026-06-28
updated: 2026-06-28
nature: knowledge
excrtx_type: fact
confidence: high
sources: [local://fixture]
---

# Entrada MCP

Corpo via servidor MCP.
"""

INDEX_TEMPLATE = """---
type: context
title: Índice — demo
description: Índice de teste
tags: [index]
timestamp: 2026-06-26
class: perene
created_at: 2026-06-26T00:00:00Z
---

# demo

### Knowledge
"""

LOG_TEMPLATE = """---
type: context
title: Log — demo
description: Log de teste
tags: [log]
timestamp: 2026-06-26
class: perene
created_at: 2026-06-26T00:00:00Z
---

# Log — demo
"""


def seed_acervo(root: Path, slug: str = "demo") -> Path:
    micro = root / "micro" / slug
    (micro / "knowledge").mkdir(parents=True)
    meta = micro / "_meta"
    meta.mkdir(parents=True)
    (meta / "index.md").write_text(INDEX_TEMPLATE, encoding="utf-8")
    (meta / "log.md").write_text(LOG_TEMPLATE, encoding="utf-8")
    return micro


def run(coro):
    return asyncio.run(coro)


def test_server_registers_expected_tools():
    from acervo_mcp_server import create_server  # pyright: ignore[reportMissingImports]

    server = create_server()
    tools = run(server.list_tools())
    names = {tool.name for tool in tools}

    assert {
        "acervo_list_microversos",
        "acervo_search",
        "acervo_read_page",
        "acervo_prepare_write",
        "acervo_commit_write",
        "acervo_create_entry",
        "acervo_update_entry",
        "acervo_validate_scope",
        "acervo_validate_frontmatter",
        "acervo_export_microverso",
    }.issubset(names)


def test_prepare_and_commit_tools_roundtrip(tmp_path: Path):
    from acervo_mcp_server import create_server  # pyright: ignore[reportMissingImports]

    acervo_root = tmp_path / "acervo"
    seed_acervo(acervo_root, slug="demo")
    server = create_server()

    prepared = run(
        server.call_tool(
            "acervo_prepare_write",
            {
                "acervo_root": str(acervo_root),
                "microverso": "demo",
                "nature": "knowledge",
                "title": "Entrada MCP",
            },
        )
    ).structured_content

    assert prepared["status"] == "ok"
    receipt = prepared["receipt"]
    assert receipt["status"] == "prepared"

    committed = run(
        server.call_tool(
            "acervo_commit_write",
            {
                "receipt": receipt,
                "content": ENTRY_MARKDOWN,
                "entry_type": "CREATED",
                "description": "entrada criada pelo servidor mcp",
            },
        )
    ).structured_content

    assert committed["status"] == "ok"
    assert committed["receipt"]["status"] == "committed"

    target = Path(committed["receipt"]["target_path"])
    assert target.exists()
    index_text = (acervo_root / "micro" / "demo" / "_meta" / "index.md").read_text(encoding="utf-8")
    assert "micro/demo/knowledge/entrada-mcp.md" in index_text
    log_text = (acervo_root / "micro" / "demo" / "_meta" / "log.md").read_text(encoding="utf-8")
    assert "entrada criada pelo servidor mcp" in log_text


def test_validate_scope_reports_cross_microverso_error(tmp_path: Path):
    from acervo_mcp_server import create_server  # pyright: ignore[reportMissingImports]

    acervo_root = tmp_path / "acervo"
    seed_acervo(acervo_root, slug="demo")
    seed_acervo(acervo_root, slug="outro")
    server = create_server()

    result = run(
        server.call_tool(
            "acervo_validate_scope",
            {
                "acervo_root": str(acervo_root),
                "active_microverso": "demo",
                "target_path": str(acervo_root / "micro" / "outro" / "knowledge" / "fora.md"),
            },
        )
    ).structured_content

    assert result["status"] == "error"
    assert result["result"]["allowed"] is False
    assert result["result"]["reason"] == "cross_microverso_write_blocked"


def test_self_test_reports_registered_tools(tmp_path: Path):
    from acervo_mcp_server import run_self_test  # pyright: ignore[reportMissingImports]

    acervo_root = tmp_path / "acervo"
    seed_acervo(acervo_root, slug="demo")

    result = run_self_test(acervo_root=acervo_root)

    assert result["ok"] is True
    assert result["tool_count"] >= 10
    assert "acervo_prepare_write" in result["tools"]
