from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "docbrain_to_acervo.py"
VALIDATOR = REPO_ROOT / "scripts" / "validate_frontmatter.py"
REAL_DOCBRAIN = Path("/home/elder/projetos/projetob/docbrain")


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


def run_adapter(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
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


def make_fake_npm(bin_dir: Path) -> None:
    npm = bin_dir / "npm"
    npm.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        "args = sys.argv[1:]\n"
        "if args[:7] == ['run','--silent','cli','--','api','health','--output'] and args[7:] == ['json']:\n"
        "    print(json.dumps({'ok': True, 'api_version': 'docbrain.cli.v1', 'command': 'health'}))\n"
        "    raise SystemExit(0)\n"
        "if args[:7] == ['run','--silent','cli','--','api','parse','create']:\n"
        "    print(json.dumps({\n"
        "        'ok': True,\n"
        "        'api_version': 'docbrain.cli.v1',\n"
        "        'command': 'parse.create',\n"
        "        'request_id': 'req_test',\n"
        "        'job': {'job_id': 'job_test', 'status': 'completed'},\n"
        "        'data': {\n"
        "            'document_id': 'sha256:test',\n"
        "            'document': {'filename': 'sample.md', 'extension': '.md', 'size_bytes': 123, 'extractor': 'text'},\n"
        "            'sections': [{'id': 'section-0', 'title': 'Resumo', 'text': 'Conteúdo de teste'}],\n"
        "            'tables': [{'id': 'table-0', 'source': 'markdown', 'columns': ['coluna', 'valor'], 'rows': [{'coluna': 'A', 'valor': 1}], 'row_count': 1}]\n"
        "        }\n"
        "    }))\n"
        "    raise SystemExit(0)\n"
        "print('unexpected args', args, file=sys.stderr)\n"
        "raise SystemExit(9)\n",
        encoding="utf-8",
    )
    npm.chmod(npm.stat().st_mode | stat.S_IEXEC)


class TestDocbrainToAcervo:
    def test_fake_docbrain_writes_markdown_and_updates_index(self, tmp_path: Path):
        acervo_root = tmp_path / "acervo"
        seed_acervo(acervo_root)
        input_file = tmp_path / "sample.md"
        input_file.write_text("# Relatório\n\nLinha 1\n", encoding="utf-8")

        fake_docbrain = tmp_path / "docbrain"
        fake_docbrain.mkdir()
        fake_bin = tmp_path / "bin"
        fake_bin.mkdir()
        make_fake_npm(fake_bin)

        result = run_adapter(
            "--input", str(input_file),
            "--microverso", "demo",
            "--acervo-root", str(acervo_root),
            "--docbrain-dir", str(fake_docbrain),
            env={"PATH": f"{fake_bin}:{os.environ['PATH']}"},
        )

        assert result.returncode == 0, result.stderr or result.stdout
        payload = json.loads(result.stdout)
        assert payload["ok"] is True
        assert payload["document_id"] == "sha256:test"
        assert payload["tables"] == 1

        output_file = Path(payload["output_file"])
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "docbrain_document_id: sha256:test" in content
        assert "## Seções" in content
        assert "## Tabelas" in content
        assert "| coluna | valor |" in content

        validator = subprocess.run(
            [sys.executable, str(VALIDATOR), "--file", str(output_file)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO_ROOT,
        )
        assert validator.returncode == 0, validator.stdout + validator.stderr

        index_text = (acervo_root / "micro" / "demo" / "_meta" / "index.md").read_text(encoding="utf-8")
        assert payload["relative_output"] in index_text

        log_text = (acervo_root / "micro" / "demo" / "_meta" / "log.md").read_text(encoding="utf-8")
        assert "CREATED:" in log_text
        assert payload["relative_output"] in log_text


@pytest.mark.slow
def test_real_docbrain_smoke_on_markdown_fixture(tmp_path: Path):
    if not REAL_DOCBRAIN.exists():
        pytest.skip("DocBrain real não disponível neste runtime")

    acervo_root = tmp_path / "acervo"
    seed_acervo(acervo_root)
    input_file = tmp_path / "fixture.md"
    input_file.write_text("# Fixture\n\nEste é um documento curto de teste.\n", encoding="utf-8")

    result = run_adapter(
        "--input", str(input_file),
        "--microverso", "demo",
        "--acervo-root", str(acervo_root),
        "--docbrain-dir", str(REAL_DOCBRAIN),
    )

    assert result.returncode == 0, result.stderr or result.stdout
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["docbrain_dir"] == str(REAL_DOCBRAIN)
    assert payload["sections"] >= 1

    output_file = Path(payload["output_file"])
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "docbrain_document_id:" in content
    assert "## Provenance" in content
