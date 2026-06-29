from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from acervo_semantic_core import commit_write, guard_write_scope, prepare_write  # pyright: ignore[reportMissingImports]

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


def build_markdown(title: str = "Teste semântico") -> str:
    frontmatter = {
        "type": "knowledge",
        "title": title,
        "description": "Entrada de teste para o semantic core.",
        "tags": ["teste", "semantic-core"],
        "timestamp": "2026-06-28",
        "class": "volátil",
        "created_at": "2026-06-28T00:00:00Z",
        "created": "2026-06-28",
        "updated": "2026-06-28",
        "nature": "knowledge",
        "excrtx_type": "fact",
        "confidence": "medium",
        "sources": ["local://fixture"],
    }
    return "---\n" + yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip() + "\n---\n\n# Teste semântico\n\nCorpo da entrada.\n"


class TestAcervoSemanticCore:
    def test_prepare_and_commit_write_updates_index_and_log(self, tmp_path: Path):
        acervo_root = tmp_path / "acervo"
        seed_acervo(acervo_root, slug="demo")

        prepared = prepare_write(
            acervo_root=acervo_root,
            microverso="demo",
            nature="knowledge",
            filename="teste-semantic-core.md",
            active_microverso="demo",
        )

        assert prepared["status"] == "prepared"
        assert prepared["relative_output"] == "micro/demo/knowledge/teste-semantic-core.md"

        committed = commit_write(
            prepared,
            content=build_markdown(),
            entry_type="CREATED",
            description="teste do semantic core",
        )

        assert committed["status"] == "committed"
        target_path = Path(committed["target_path"])
        assert target_path.exists()
        assert "Teste semântico" in target_path.read_text(encoding="utf-8")

        index_text = (acervo_root / "micro" / "demo" / "_meta" / "index.md").read_text(encoding="utf-8")
        assert "micro/demo/knowledge/teste-semantic-core.md" in index_text

        log_text = (acervo_root / "micro" / "demo" / "_meta" / "log.md").read_text(encoding="utf-8")
        assert "CREATED: micro/demo/knowledge/teste-semantic-core.md (volátil) — teste do semantic core" in log_text

    def test_guard_write_scope_blocks_cross_microverso_target(self, tmp_path: Path):
        acervo_root = tmp_path / "acervo"
        seed_acervo(acervo_root, slug="alpha")
        seed_acervo(acervo_root, slug="beta")

        target = acervo_root / "micro" / "beta" / "knowledge" / "fora.md"
        with pytest.raises(RuntimeError, match="fora do microverso ativo"):
            guard_write_scope(
                target,
                active_microverso="alpha",
                acervo_root=acervo_root,
            )
