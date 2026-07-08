"""Phase 4 write-side — intention lifecycle sweep (05-object-model §3, 08 §6).

Covers the schema fix (intention terminal statuses), the governed mark_intention
verb, and the acervoctl sweep-intentions orchestration (dry-run vs --apply).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
TOOLS = REPO / "acervo" / "global" / "tools"
ACERVOCTL = SCRIPTS / "acervoctl.py"
VALIDATOR = SCRIPTS / "validate_frontmatter.py"
FIXTURE = REPO / "tests" / "memory-eval" / "fixture" / "acervo"

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(TOOLS))

import acervo_catalog  # noqa: E402
import acervo_semantic_core as core  # noqa: E402


def _intention(title: str, description: str, due: str, status: str = "active") -> str:
    return (
        "---\n"
        "schema: acervo/v0.2\n"
        "type: intention\n"
        f"title: {title}\n"
        f"description: {description}\n"
        "tags: [test]\n"
        "class: volátil\n"
        "epistemic: intention\n"
        f"status: {status}\n"
        "created_at: 2026-01-01T00:00:00Z\n"
        f"due: {due}\n"
        "---\n\n"
        f"# {title}\n"
    )


@pytest.fixture()
def acervo(tmp_path: Path) -> Path:
    root = tmp_path / "acervo"
    shutil.copytree(FIXTURE, root)
    intents = root / "micro" / "operacoes" / "intentions"
    intents.mkdir(exist_ok=True)
    (intents / "vencida.md").write_text(
        _intention("Enviar proposta", "vencida", "2026-06-01"), encoding="utf-8")
    (intents / "hoje.md").write_text(
        _intention("Ligar hoje", "due today", "2026-07-08"), encoding="utf-8")
    (intents / "futura.md").write_text(
        _intention("Revisar contrato", "futura", "2027-01-01"), encoding="utf-8")
    acervo_catalog.build_catalog(root)
    return root


# ---------------------------------------------------------------- schema fix

def _validate(path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--file", str(path)],
        capture_output=True, text=True,
    )


def test_validator_accepts_intention_terminal_statuses(tmp_path: Path) -> None:
    for state in ("done", "dropped", "expired"):
        f = tmp_path / f"{state}.md"
        f.write_text(_intention("Intenção", "encerrada", "2026-06-01", status=state), encoding="utf-8")
        result = _validate(f)
        assert result.returncode == 0, f"{state} should validate:\n{result.stdout}"


def test_validator_rejects_terminal_status_on_non_intention(tmp_path: Path) -> None:
    # done|dropped|expired are intention-only; a knowledge file must not claim them.
    f = tmp_path / "k.md"
    f.write_text(
        "---\nschema: acervo/v0.2\ntype: knowledge\ntitle: X\ndescription: y\n"
        "tags: [t]\nclass: volátil\nstatus: done\ncreated_at: 2026-01-01T00:00:00Z\n---\n\n# X\n",
        encoding="utf-8",
    )
    result = _validate(f)
    assert result.returncode != 0
    assert "V2-017" in result.stdout


# ------------------------------------------------------------- mark_intention

def test_mark_intention_transitions_and_journals(acervo: Path) -> None:
    target = acervo / "micro" / "operacoes" / "intentions" / "vencida.md"
    out = core.mark_intention(
        acervo_root=acervo, path=target, state="expired",
        reason="prazo passou sem entrega", today="2026-07-08")
    assert out["ok"] and out["state"] == "expired" and out["resolved_at"] == "2026-07-08"
    text = target.read_text(encoding="utf-8")
    assert "status: expired" in text
    assert "resolved_at: 2026-07-08" in text
    assert "prazo passou sem entrega" in text
    log = (acervo / "micro" / "operacoes" / "_meta" / "log.md").read_text(encoding="utf-8")
    assert "UPDATED: micro/operacoes/intentions/vencida.md — intention expired" in log
    # File still exists — intentions are never deleted (relationship history).
    assert target.is_file()


def test_mark_intention_idempotent_when_terminal(acervo: Path) -> None:
    target = acervo / "micro" / "operacoes" / "intentions" / "vencida.md"
    core.mark_intention(acervo_root=acervo, path=target, state="done", reason="entregue", today="2026-07-08")
    again = core.mark_intention(acervo_root=acervo, path=target, state="expired", reason="x", today="2026-07-08")
    assert again["unchanged"] is True and again["state"] == "done"


def test_mark_intention_rejects_non_intention(acervo: Path) -> None:
    other = acervo / "micro" / "operacoes" / "knowledge" / "nao-intencao.md"
    other.parent.mkdir(parents=True, exist_ok=True)
    other.write_text(
        "---\nschema: acervo/v0.2\ntype: knowledge\ntitle: X\ndescription: y\n"
        "tags: [t]\nclass: volátil\nstatus: active\ncreated_at: 2026-01-01T00:00:00Z\n---\n\n# X\n",
        encoding="utf-8")
    with pytest.raises(RuntimeError, match="não é uma intenção"):
        core.mark_intention(acervo_root=acervo, path=other, state="done", reason="x")


def test_mark_intention_rejects_bad_state_and_empty_reason(acervo: Path) -> None:
    target = acervo / "micro" / "operacoes" / "intentions" / "futura.md"
    with pytest.raises(RuntimeError, match="state inválido"):
        core.mark_intention(acervo_root=acervo, path=target, state="cancelled", reason="x")
    with pytest.raises(RuntimeError, match="reason é obrigatório"):
        core.mark_intention(acervo_root=acervo, path=target, state="done", reason="   ")


# ----------------------------------------------------------- sweep-intentions

def _sweep(acervo: Path, *extra: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(ACERVOCTL), "sweep-intentions",
         "--acervo-root", str(acervo), "--today", "2026-07-08", *extra],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


def test_sweep_dry_run_reports_only_overdue(acervo: Path) -> None:
    result = _sweep(acervo)
    assert result["applied"] is False
    paths = [e["path"] for e in result["expired"]]
    # Overdue 'vencida' is a candidate; due-today and future never are.
    assert any(p.endswith("vencida.md") for p in paths)
    assert not any(p.endswith("hoje.md") or p.endswith("futura.md") for p in paths)
    assert all(e.get("would_expire") for e in result["expired"])
    # Nothing was written in dry-run.
    text = (acervo / "micro" / "operacoes" / "intentions" / "vencida.md").read_text(encoding="utf-8")
    assert "status: active" in text


def test_sweep_apply_expires_overdue_only(acervo: Path) -> None:
    result = _sweep(acervo, "--apply")
    assert result["applied"] is True and result["candidates"] >= 1
    assert not result["skipped"]
    intents = acervo / "micro" / "operacoes" / "intentions"
    assert "status: expired" in (intents / "vencida.md").read_text(encoding="utf-8")
    # due-today and future intentions remain active.
    assert "status: active" in (intents / "hoje.md").read_text(encoding="utf-8")
    assert "status: active" in (intents / "futura.md").read_text(encoding="utf-8")
    # Re-running finds nothing (naturally idempotent: expired ∉ active queue).
    acervo_catalog.build_catalog(acervo)
    assert _sweep(acervo, "--apply")["candidates"] == 0
