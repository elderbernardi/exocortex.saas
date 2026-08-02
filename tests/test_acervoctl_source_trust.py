import json, subprocess, sys, os, shutil
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
ACERVOCTL = REPO / "scripts" / "acervoctl.py"
FIXTURE = REPO / "tests" / "memory-eval" / "fixture" / "acervo"

sys.path.insert(0, str(REPO / "scripts"))
import acervo_semantic_core as core

INDEX_TEMPLATE = """---
type: context
title: Índice — {slug}
description: Índice de teste
tags: [index]
timestamp: 2026-06-26
class: perene
created_at: 2026-06-26T00:00:00Z
---

# {slug}

### Knowledge
"""

LOG_TEMPLATE = """---
type: context
title: Log — {slug}
description: Log de teste
tags: [log]
timestamp: 2026-06-26
class: perene
created_at: 2026-06-26T00:00:00Z
---

# Log — {slug}
"""

def _run(args, acervo_root):
    env = {**os.environ, "ACERVO_ROOT": str(acervo_root)}
    return subprocess.run([sys.executable, str(ACERVOCTL), *args],
                          capture_output=True, text=True, env=env)

@pytest.fixture()
def acervo(tmp_path: Path) -> Path:
    """Create an acervo fixture for testing by copying the test fixture and building catalog."""
    root = tmp_path / "acervo"
    shutil.copytree(FIXTURE, root)
    catalog = core.load_tool_module(root, "acervo_catalog")
    catalog.build_catalog(root)

    # Ensure all microversos have _meta/index.md and log.md files
    for micro_dir in (root / "micro").iterdir():
        if micro_dir.is_dir():
            meta = micro_dir / "_meta"
            meta.mkdir(parents=True, exist_ok=True)
            slug = micro_dir.name
            (meta / "index.md").write_text(INDEX_TEMPLATE.format(slug=slug), encoding="utf-8")
            (meta / "log.md").write_text(LOG_TEMPLATE.format(slug=slug), encoding="utf-8")

    return root

def test_prepare_write_carries_untrusted_into_receipt(acervo: Path):
    r = _run(["prepare-write", "--acervo-root", str(acervo),
              "--microverso", "cliente-norte", "--nature", "knowledge",
              "--title", "Nota de teste", "--source-trust", "untrusted"], acervo)
    assert r.returncode == 0, f"stderr: {r.stderr}\nstdout: {r.stdout}"
    receipt = json.loads(r.stdout)
    assert receipt["source_trust"] == "untrusted"

def test_commit_write_untrusted_forces_status_draft(acervo: Path, tmp_path: Path):
    # prepare with untrusted, then commit valid OKF content, expect status: draft on disk
    pr = _run(["prepare-write", "--acervo-root", str(acervo), "--microverso", "cliente-norte",
               "--nature", "knowledge", "--title", "Nota de teste",
               "--source-trust", "untrusted", "--receipt-out", str(tmp_path/"r.json")], acervo)
    assert pr.returncode == 0, f"stderr: {pr.stderr}\nstdout: {pr.stdout}"
    content = (
        "---\nschema: acervo/v0.2\ntype: knowledge\ntitle: Nota de teste\n"
        "description: nota\ntags: []\ncreated_at: 2026-08-01T00:00:00Z\nclass: volátil\n"
        "status: active\nepistemic: observation\nconfidence: likely\n"
        "sources:\n  - type: agent-inference\n    ref: t1\nobserved_at: 2026-08-01\n"
        "extraction: agent\n---\ncorpo\n")
    (tmp_path/"c.md").write_text(content, encoding="utf-8")
    cm = _run(["commit-write", "--receipt", str(tmp_path/"r.json"),
               "--content-file", str(tmp_path/"c.md"), "--description", "nota"], acervo)
    assert cm.returncode == 0, f"stderr: {cm.stderr}\nstdout: {cm.stdout}"
    committed = json.loads(cm.stdout)
    on_disk = Path(committed["target_path"]).read_text(encoding="utf-8")
    assert "status: draft" in on_disk  # trust gate forced it

def test_commit_write_rejects_loosening_trust(acervo: Path, tmp_path: Path):
    """Verify that commit-write --source-trust rejects loosening (only allows tightening).

    Receipt prepared with untrusted (most restrictive) cannot be loosened to agent.
    Commit must return non-zero and reject the change.
    """
    # Step 1: prepare with untrusted (restrictive)
    pr = _run(["prepare-write", "--acervo-root", str(acervo), "--microverso", "cliente-norte",
               "--nature", "knowledge", "--title", "Nota de teste",
               "--source-trust", "untrusted", "--receipt-out", str(tmp_path/"r.json")], acervo)
    assert pr.returncode == 0, f"stderr: {pr.stderr}\nstdout: {pr.stdout}"

    # Step 2: try to commit with --source-trust agent (more trusting = loosening)
    content = (
        "---\nschema: acervo/v0.2\ntype: knowledge\ntitle: Nota de teste\n"
        "description: nota\ntags: []\ncreated_at: 2026-08-01T00:00:00Z\nclass: volátil\n"
        "status: active\nepistemic: observation\nconfidence: likely\n"
        "sources:\n  - type: agent-inference\n    ref: t1\nobserved_at: 2026-08-01\n"
        "extraction: agent\n---\ncorpo\n")
    (tmp_path/"c.md").write_text(content, encoding="utf-8")
    cm = _run(["commit-write", "--receipt", str(tmp_path/"r.json"),
               "--content-file", str(tmp_path/"c.md"), "--description", "nota",
               "--source-trust", "agent"], acervo)

    # Step 3: Expect non-zero exit (rejection)
    assert cm.returncode != 0, f"Expected rejection but got success. stdout: {cm.stdout}"
    assert "afrouxaria" in cm.stdout or "afrouxaria" in cm.stderr, \
        f"Expected error message about loosening, got: stderr={cm.stderr}, stdout={cm.stdout}"

def test_commit_write_allows_tightening_trust(acervo: Path, tmp_path: Path):
    """Verify that commit-write --source-trust allows tightening (only rejects loosening).

    Receipt prepared with agent can be tightened to untrusted. Commit must succeed.
    """
    # Step 1: prepare with agent (moderate trust)
    pr = _run(["prepare-write", "--acervo-root", str(acervo), "--microverso", "cliente-norte",
               "--nature", "knowledge", "--title", "Nota de teste",
               "--source-trust", "agent", "--receipt-out", str(tmp_path/"r.json")], acervo)
    assert pr.returncode == 0, f"stderr: {pr.stderr}\nstdout: {pr.stdout}"

    # Step 2: commit with --source-trust untrusted (more restrictive = tightening)
    content = (
        "---\nschema: acervo/v0.2\ntype: knowledge\ntitle: Nota de teste\n"
        "description: nota\ntags: []\ncreated_at: 2026-08-01T00:00:00Z\nclass: volátil\n"
        "status: active\nepistemic: observation\nconfidence: likely\n"
        "sources:\n  - type: agent-inference\n    ref: t1\nobserved_at: 2026-08-01\n"
        "extraction: agent\n---\ncorpo\n")
    (tmp_path/"c.md").write_text(content, encoding="utf-8")
    cm = _run(["commit-write", "--receipt", str(tmp_path/"r.json"),
               "--content-file", str(tmp_path/"c.md"), "--description", "nota",
               "--source-trust", "untrusted"], acervo)

    # Step 3: Expect success (tightening is allowed)
    assert cm.returncode == 0, f"stderr: {cm.stderr}\nstdout: {cm.stdout}"
    committed = json.loads(cm.stdout)
    # With untrusted, file should have status: draft
    on_disk = Path(committed["target_path"]).read_text(encoding="utf-8")
    assert "status: draft" in on_disk
