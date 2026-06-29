from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "acervoctl.py"
VALIDATOR = REPO_ROOT / "scripts" / "validate_frontmatter.py"

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

ENTRY_TEMPLATE = """---
type: knowledge
title: Documento Base
description: Entrada para busca
tags: [teste, busca]
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

# Documento Base

Termo especial de busca: macroverso.
"""


def seed_acervo(root: Path, slug: str = "demo") -> Path:
    micro = root / "micro" / slug
    (micro / "knowledge").mkdir(parents=True)
    meta = micro / "_meta"
    meta.mkdir(parents=True)
    (meta / "index.md").write_text(INDEX_TEMPLATE, encoding="utf-8")
    (meta / "log.md").write_text(LOG_TEMPLATE, encoding="utf-8")
    return micro


def run_cli(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        env=merged_env,
    )


class TestAcervoCtl:
    def test_list_microversos_returns_sorted_slugs(self, tmp_path: Path):
        acervo_root = tmp_path / "acervo"
        seed_acervo(acervo_root, slug="zeta")
        seed_acervo(acervo_root, slug="alpha")

        result = run_cli("list-microversos", "--acervo-root", str(acervo_root))

        assert result.returncode == 0, result.stderr or result.stdout
        payload = json.loads(result.stdout)
        assert payload["ok"] is True
        assert payload["microversos"] == ["alpha", "zeta"]

    def test_search_returns_matching_entry(self, tmp_path: Path):
        acervo_root = tmp_path / "acervo"
        micro = seed_acervo(acervo_root, slug="demo")
        entry = micro / "knowledge" / "documento-base.md"
        entry.write_text(ENTRY_TEMPLATE, encoding="utf-8")

        result = run_cli("search", "--acervo-root", str(acervo_root), "--query", "macroverso")

        assert result.returncode == 0, result.stderr or result.stdout
        payload = json.loads(result.stdout)
        assert payload["ok"] is True
        assert payload["count"] >= 1
        assert payload["matches"][0]["path"] == "micro/demo/knowledge/documento-base.md"
        assert "macroverso" in payload["matches"][0]["line"].lower()

    def test_prepare_and_commit_write_roundtrip(self, tmp_path: Path):
        acervo_root = tmp_path / "acervo"
        seed_acervo(acervo_root, slug="demo")
        receipt_path = tmp_path / "receipt.json"
        content_path = tmp_path / "entry.md"
        content = {
            "type": "knowledge",
            "title": "Nova Entrada",
            "description": "Entrada criada via acervoctl.",
            "tags": ["teste", "cli"],
            "timestamp": "2026-06-28",
            "class": "volátil",
            "created_at": "2026-06-28T00:00:00Z",
            "created": "2026-06-28",
            "updated": "2026-06-28",
            "nature": "knowledge",
            "excrtx_type": "fact",
            "confidence": "high",
            "sources": ["local://fixture"],
        }
        content_path.write_text(
            "---\n"
            + yaml.safe_dump(content, sort_keys=False, allow_unicode=True).strip()
            + "\n---\n\n# Nova Entrada\n\nCorpo via CLI.\n",
            encoding="utf-8",
        )

        prepare = run_cli(
            "prepare-write",
            "--acervo-root",
            str(acervo_root),
            "--microverso",
            "demo",
            "--nature",
            "knowledge",
            "--title",
            "Nova Entrada",
            "--receipt-out",
            str(receipt_path),
        )
        assert prepare.returncode == 0, prepare.stderr or prepare.stdout
        prepared = json.loads(prepare.stdout)
        assert prepared["status"] == "prepared"
        assert receipt_path.exists()

        commit = run_cli(
            "commit-write",
            "--receipt",
            str(receipt_path),
            "--content-file",
            str(content_path),
            "--entry-type",
            "CREATED",
            "--description",
            "entrada criada por teste",
        )
        assert commit.returncode == 0, commit.stderr or commit.stdout
        committed = json.loads(commit.stdout)
        assert committed["status"] == "committed"

        output_path = Path(committed["target_path"])
        assert output_path.exists()
        validator = subprocess.run(
            [sys.executable, str(VALIDATOR), "--file", str(output_path)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert validator.returncode == 0, validator.stdout + validator.stderr

        index_text = (acervo_root / "micro" / "demo" / "_meta" / "index.md").read_text(encoding="utf-8")
        assert "micro/demo/knowledge/nova-entrada.md" in index_text
        log_text = (acervo_root / "micro" / "demo" / "_meta" / "log.md").read_text(encoding="utf-8")
        assert "CREATED: micro/demo/knowledge/nova-entrada.md (volátil) — entrada criada por teste" in log_text

    def test_export_microverso_builds_package(self, tmp_path: Path):
        acervo_root = tmp_path / "acervo"
        seed_acervo(acervo_root, slug="demo")
        out_dir = tmp_path / "out"

        result = run_cli(
            "export-microverso",
            "--acervo-root",
            str(acervo_root),
            "--slug",
            "demo",
            "--out",
            str(out_dir),
        )

        assert result.returncode == 0, result.stderr or result.stdout
        payload = json.loads(result.stdout)
        assert payload["ok"] is True
        package_path = Path(payload["package_path"])
        assert package_path.exists()
        assert package_path.name.startswith("demo-v")
