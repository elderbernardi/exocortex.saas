from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


CORE = Path(__file__).parents[1] / "skills/excrtx-integrate-databrain/scripts/databrain_ops_core.py"


def load_core():
    spec = importlib.util.spec_from_file_location("databrain_ops_core", CORE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_capabilities_have_no_arbitrary_shell():
    core = load_core()
    caps = core.capabilities()
    assert caps["api_version"] == "projetob.databrain.ops.v1"
    assert caps["arbitrary_shell"] is False
    assert {item["name"] for item in caps["operations"]} == set(core.OPERATIONS)


def test_external_writes_require_approval():
    core = load_core()
    assert core.OPERATIONS["publish"].approval_required is True
    assert core.OPERATIONS["incremental_publish"].approval_required is True
    assert core.OPERATIONS["incremental_prepare"].approval_required is False
    assert "publish_retry" not in core.OPERATIONS


def test_operation_command_is_fixed_and_container_scoped(monkeypatch):
    core = load_core()
    monkeypatch.setenv("DATABRAIN_CONTAINER", "db-prod")
    command = core.operation_command("dry_run")
    assert command[:6] == ["sudo", "-n", "docker", "exec", "db-prod", "node"]
    assert command[-1] == "--dry-run"
    with pytest.raises(ValueError):
        core.operation_command("shell")


def test_oracle_operations_use_production_ingest_wrapper(monkeypatch):
    core = load_core()
    monkeypatch.setenv("DATABRAIN_INGEST_WRAPPER", "/srv/databrain/ops/ingest-run.sh")
    command = core.operation_command("incremental_prepare")
    assert command[:4] == ["sudo", "-n", "/srv/databrain/ops/ingest-run.sh", "--"]
    assert "--fetch-oracle" in command
    assert command[:5] != ["sudo", "-n", "docker", "exec", core.container_name()]


def test_receipt_is_immutable_and_one_time(tmp_path, monkeypatch):
    core = load_core()
    monkeypatch.setenv("DATABRAIN_OPS_ROOT", str(tmp_path))
    receipt = core.prepare_operation("cold", requested_by="test")
    assert receipt["status"] == "prepared"
    assert receipt["approval_required"] is False
    persisted = json.loads((tmp_path / receipt["receipt_id"] / "receipt.json").read_text())
    assert persisted["command_preview"] == ["node", "dist/cli/index.js", "run", "cold"]


def test_receipt_id_rejects_path_traversal(tmp_path, monkeypatch):
    core = load_core()
    monkeypatch.setenv("DATABRAIN_OPS_ROOT", str(tmp_path))
    with pytest.raises(ValueError):
        core.load_receipt("../../etc/passwd")


def test_sanitize_payload_removes_config_snapshot_and_redacts_nested_secrets():
    core = load_core()
    payload = {
        "id": "run-1",
        "config_snapshot": {"database": {"password": "clear"}},
        "safe": {"service_key": "clear", "count": 2},
        "rows": [{"apiKey": "clear", "name": "ok"}],
    }
    clean = core.sanitize_payload(payload)
    assert "config_snapshot" not in clean
    assert clean["safe"] == {"service_key": "[REDACTED]", "count": 2}
    assert clean["rows"] == [{"apiKey": "[REDACTED]", "name": "ok"}]
