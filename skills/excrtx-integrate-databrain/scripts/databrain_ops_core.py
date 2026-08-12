#!/usr/bin/env python3
"""Core governado da ponte operacional Exocórtex ↔ DataBrain.

Sem shell arbitrário: toda execução resolve para uma operação nomeada e uma
lista fixa de argumentos do CLI oficial do DataBrain dentro do container ativo.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

DEFAULT_CONTAINER = "databrain-databrain-1"
DEFAULT_API_URL = "http://127.0.0.1:8000"
DEFAULT_OPS_ROOT = Path.home() / ".hermes" / "runs" / "databrain-ops"
RECEIPT_TTL_HOURS = 24
MAX_RUNTIME_SECONDS = 4 * 60 * 60
SENSITIVE_KEY_PATTERN = re.compile(
    r"(?:pass(?:word)?|secret|token|api[_-]?key|service[_-]?key|private[_-]?key|credential|database_url)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class OperationSpec:
    name: str
    description: str
    effect: str
    approval_required: bool
    command: tuple[str, ...]


OPERATIONS: dict[str, OperationSpec] = {
    "dry_run": OperationSpec(
        "dry_run",
        "Valida o plano do pipeline completo sem processar nem publicar.",
        "read_only",
        False,
        ("node", "dist/cli/index.js", "run", "full", "--trigger", "api", "--dry-run"),
    ),
    "ingest_inbox": OperationSpec(
        "ingest_inbox",
        "Ingere arquivos já presentes na inbox para a camada Bronze.",
        "local_write",
        False,
        ("node", "dist/cli/index.js", "ingest"),
    ),
    "cold": OperationSpec(
        "cold",
        "Executa Ingestion → Cleansing → Cold sobre dados locais.",
        "local_write",
        False,
        ("node", "dist/cli/index.js", "run", "cold"),
    ),
    "hot": OperationSpec(
        "hot",
        "Executa o Hot Engine e gera inteligência com LLM sem publicar.",
        "local_write_with_llm_cost",
        False,
        ("node", "dist/cli/index.js", "run", "hot"),
    ),
    "judge": OperationSpec(
        "judge",
        "Executa o LLM-as-Judge sobre a quarentena local sem publicar.",
        "local_write_with_llm_cost",
        False,
        ("node", "dist/cli/index.js", "run", "judge"),
    ),
    "incremental_prepare": OperationSpec(
        "incremental_prepare",
        "Busca incremental no Oracle e atualiza Bronze/Silver/Gold, sem LLM e sem Supabase.",
        "source_read_local_write",
        False,
        (
            "node", "dist/cli/index.js", "run", "full", "--trigger", "api",
            "--fetch-oracle", "--skip-hot", "--skip-publisher",
        ),
    ),
    "incremental_refresh_prepare": OperationSpec(
        "incremental_refresh_prepare",
        "Busca incremental no Oracle, força refresh das dimensões e atualiza Gold; sem LLM/Supabase.",
        "source_read_local_write",
        False,
        (
            "node", "dist/cli/index.js", "run", "full", "--trigger", "api",
            "--fetch-oracle", "--refresh-dims", "--skip-hot", "--skip-publisher",
        ),
    ),
    "incremental_ai_prepare": OperationSpec(
        "incremental_ai_prepare",
        "Busca incremental, atualiza o lake e executa Hot/Judge, sem publicar no Supabase.",
        "source_read_local_write_with_llm_cost",
        False,
        (
            "node", "dist/cli/index.js", "run", "full", "--trigger", "api",
            "--fetch-oracle", "--skip-publisher",
        ),
    ),
    "incremental_publish": OperationSpec(
        "incremental_publish",
        "Executa o pipeline incremental completo e publica o resultado no Sales-AI/Supabase.",
        "external_write",
        True,
        ("node", "dist/cli/index.js", "run", "full", "--trigger", "api", "--fetch-oracle"),
    ),
    "publish": OperationSpec(
        "publish",
        "Publica os artefatos Gold/Hot/Judge atuais no Sales-AI/Supabase.",
        "external_write",
        True,
        ("node", "dist/cli/index.js", "run", "publish"),
    ),
    "publish_retry": OperationSpec(
        "publish_retry",
        "Reexecuta publicação de artefatos que falharam anteriormente.",
        "external_write",
        True,
        ("node", "dist/cli/index.js", "run", "publish", "--retry-failed"),
    ),
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().isoformat()


def ops_root() -> Path:
    path = Path(os.getenv("DATABRAIN_OPS_ROOT", str(DEFAULT_OPS_ROOT))).expanduser().resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def container_name() -> str:
    return os.getenv("DATABRAIN_CONTAINER", DEFAULT_CONTAINER)


def api_url() -> str:
    return os.getenv("DATABRAIN_API_URL", DEFAULT_API_URL).rstrip("/")


def operation_command(operation: str) -> list[str]:
    try:
        spec = OPERATIONS[operation]
    except KeyError as exc:
        raise ValueError(f"Operação não permitida: {operation}") from exc
    return ["sudo", "-n", "docker", "exec", container_name(), *spec.command]


def capabilities() -> dict[str, Any]:
    return {
        "api_version": "projetob.databrain.ops.v1",
        "execution_model": "named_operations_only",
        "arbitrary_shell": False,
        "operations": [asdict(spec) for spec in OPERATIONS.values()],
    }


def http_json(path: str, *, timeout: float = 10.0) -> Any:
    url = f"{api_url()}{path}"
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"DataBrain HTTP {exc.code} em {path}: {body[:300]}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"DataBrain indisponível em {url}: {exc}") from exc


def _scheduler_state() -> dict[str, Any]:
    proc = subprocess.run(
        [
            "sudo", "-n", "docker", "inspect", container_name(),
            "--format", "{{range .Config.Env}}{{println .}}{{end}}",
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    if proc.returncode != 0:
        return {"enabled": None, "source": "container_env", "error": proc.stderr.strip()[:300]}
    value = None
    for line in proc.stdout.splitlines():
        if line.startswith("DATABRAIN_SCHEDULER_ENABLED="):
            value = line.split("=", 1)[1].strip().lower()
            break
    enabled = value in {"1", "true", "yes", "on"} if value is not None else None
    return {
        "enabled": enabled,
        "source": "DATABRAIN_SCHEDULER_ENABLED",
        "automatic_runs": enabled is True,
    }


def health() -> dict[str, Any]:
    payload = http_json("/health")
    inspect = subprocess.run(
        ["sudo", "-n", "docker", "inspect", container_name(), "--format", "{{.State.Status}}|{{.State.Health.Status}}|{{.Config.Image}}"],
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    container = {"name": container_name(), "reachable": inspect.returncode == 0}
    if inspect.returncode == 0:
        status, health_status, image = inspect.stdout.strip().split("|", 2)
        container.update({"status": status, "health": health_status, "image": image})
    else:
        container["error"] = inspect.stderr.strip()[:300]
    return {
        "status": "ok",
        "api": payload,
        "container": container,
        "scheduler": _scheduler_state(),
    }


def sanitize_payload(value: Any, key: str | None = None) -> Any:
    """Remove snapshots e redige chaves sensíveis antes da fronteira MCP."""
    if key == "config_snapshot":
        return None
    if key and SENSITIVE_KEY_PATTERN.search(key):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {
            child_key: sanitize_payload(child_value, child_key)
            for child_key, child_value in value.items()
            if child_key != "config_snapshot"
        }
    if isinstance(value, list):
        return [sanitize_payload(item) for item in value]
    return value


def list_runs(limit: int = 10, status: str | None = None) -> dict[str, Any]:
    limit = min(max(int(limit), 1), 50)
    query = {"limit": str(limit)}
    if status:
        query["status"] = status
    rows = sanitize_payload(http_json(f"/cockpit/runs?{urllib.parse.urlencode(query)}"))
    return {"status": "ok", "count": len(rows), "runs": rows}


def get_run(run_id: str) -> dict[str, Any]:
    if not run_id or "/" in run_id or ".." in run_id:
        raise ValueError("run_id inválido")
    run = sanitize_payload(http_json(f"/cockpit/runs/{urllib.parse.quote(run_id)}"))
    return {"status": "ok", "run": run}


def list_inbox(limit: int = 50) -> dict[str, Any]:
    limit = min(max(int(limit), 1), 200)
    proc = subprocess.run(
        [
            "sudo", "-n", "find", "/srv/databrain/data/inbox", "-maxdepth", "1", "-type", "f",
            "-printf", "%f\\t%s\\t%T@\\n",
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Falha ao listar inbox: {proc.stderr.strip()[:300]}")
    files = []
    for line in proc.stdout.splitlines():
        try:
            name, size, mtime = line.split("\t", 2)
            files.append({"name": name, "size_bytes": int(size), "mtime_epoch": float(mtime)})
        except ValueError:
            continue
    files.sort(key=lambda item: item["mtime_epoch"], reverse=True)
    return {"status": "ok", "count": len(files), "files": files[:limit]}


def _receipt_path(receipt_id: str) -> Path:
    if not receipt_id.startswith("dbop_") or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789_" for c in receipt_id):
        raise ValueError("receipt_id inválido")
    return ops_root() / receipt_id / "receipt.json"


def _metadata_path(operation_id: str) -> Path:
    if not operation_id.startswith("dbop_") or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789_" for c in operation_id):
        raise ValueError("operation_id inválido")
    return ops_root() / operation_id / "operation.json"


def prepare_operation(operation: str, requested_by: str = "exocortex") -> dict[str, Any]:
    if operation not in OPERATIONS:
        raise ValueError(f"Operação não permitida: {operation}")
    spec = OPERATIONS[operation]
    receipt_id = f"dbop_{uuid4().hex}"
    directory = ops_root() / receipt_id
    directory.mkdir(mode=0o700, parents=True, exist_ok=False)
    created = utc_now()
    receipt = {
        "api_version": "projetob.databrain.ops.v1",
        "receipt_id": receipt_id,
        "operation": operation,
        "description": spec.description,
        "effect": spec.effect,
        "approval_required": spec.approval_required,
        "requested_by": requested_by,
        "created_at": created.isoformat(),
        "expires_at": (created + timedelta(hours=RECEIPT_TTL_HOURS)).isoformat(),
        "command_preview": list(spec.command),
        "status": "prepared",
    }
    _receipt_path(receipt_id).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


def load_receipt(receipt_id: str) -> dict[str, Any]:
    path = _receipt_path(receipt_id)
    if not path.exists():
        raise ValueError("Receipt inexistente")
    receipt = json.loads(path.read_text(encoding="utf-8"))
    if datetime.fromisoformat(receipt["expires_at"]) < utc_now():
        raise ValueError("Receipt expirado")
    return receipt


def _active_bridge_operations() -> list[str]:
    active = []
    for metadata in ops_root().glob("dbop_*/operation.json"):
        try:
            item = json.loads(metadata.read_text(encoding="utf-8"))
            unit = item["unit"]
            proc = subprocess.run(
                ["systemctl", "--user", "is-active", unit],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if proc.stdout.strip() in {"active", "activating", "reloading"}:
                active.append(item["operation_id"])
        except Exception:
            continue
    return active


def start_operation(receipt_id: str, approval_ref: str | None = None) -> dict[str, Any]:
    receipt = load_receipt(receipt_id)
    if receipt["status"] != "prepared":
        raise ValueError(f"Receipt já consumido: {receipt['status']}")
    spec = OPERATIONS[receipt["operation"]]
    if spec.approval_required and (not approval_ref or len(approval_ref.strip()) < 8):
        raise PermissionError("Esta operação escreve externamente e exige approval_ref pós-DRAFT.")
    active = _active_bridge_operations()
    if active:
        raise RuntimeError(f"Já existe operação da ponte em execução: {active}")
    live = health()
    if live["api"].get("status") != "ok" or live["container"].get("health") != "healthy":
        raise RuntimeError("DataBrain não está saudável; operação recusada.")

    operation_id = receipt_id
    directory = ops_root() / operation_id
    log_path = directory / "operation.log"
    unit = f"databrain-op-{operation_id.removeprefix('dbop_')[:20]}"
    command = operation_command(spec.name)
    systemd_command = [
        "systemd-run", "--user", f"--unit={unit}",
        "--property=Type=exec",
        f"--property=RuntimeMaxSec={MAX_RUNTIME_SECONDS}",
        f"--property=StandardOutput=append:{log_path}",
        f"--property=StandardError=append:{log_path}",
        *command,
    ]
    launched = subprocess.run(systemd_command, check=False, capture_output=True, text=True, timeout=30)
    if launched.returncode != 0:
        raise RuntimeError(f"Falha ao iniciar unidade: {launched.stderr.strip()[:500]}")
    metadata = {
        "api_version": "projetob.databrain.ops.v1",
        "operation_id": operation_id,
        "receipt_id": receipt_id,
        "operation": spec.name,
        "effect": spec.effect,
        "approval_required": spec.approval_required,
        "approval_ref": approval_ref.strip() if approval_ref else None,
        "unit": unit,
        "container": container_name(),
        "command": command,
        "log_path": str(log_path),
        "started_at": iso_now(),
        "status": "started",
    }
    _metadata_path(operation_id).write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    receipt["status"] = "consumed"
    receipt["consumed_at"] = iso_now()
    _receipt_path(receipt_id).write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return metadata


def _systemd_properties(unit: str) -> dict[str, str]:
    props = ["LoadState", "ActiveState", "SubState", "Result", "ExecMainCode", "ExecMainStatus", "StateChangeTimestamp"]
    proc = subprocess.run(
        ["systemctl", "--user", "show", unit, *[f"--property={p}" for p in props]],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if proc.returncode != 0:
        return {"LoadState": "not-found", "error": proc.stderr.strip()[:300]}
    return dict(line.split("=", 1) for line in proc.stdout.splitlines() if "=" in line)


def operation_status(operation_id: str) -> dict[str, Any]:
    path = _metadata_path(operation_id)
    if not path.exists():
        raise ValueError("Operação inexistente")
    metadata = json.loads(path.read_text(encoding="utf-8"))
    systemd = _systemd_properties(metadata["unit"])
    active = systemd.get("ActiveState")
    result = systemd.get("Result")
    if active in {"active", "activating", "reloading"}:
        status = "running"
    elif result == "success" and systemd.get("ExecMainStatus") == "0":
        status = "succeeded"
    elif active in {"failed", "inactive"}:
        status = "failed" if result not in {"success", ""} else "succeeded"
    else:
        status = "unknown"
    return {"status": "ok", "operation_status": status, "operation": metadata, "systemd": systemd}


def operation_logs(operation_id: str, tail_lines: int = 200) -> dict[str, Any]:
    tail_lines = min(max(int(tail_lines), 1), 1000)
    metadata = json.loads(_metadata_path(operation_id).read_text(encoding="utf-8"))
    path = Path(metadata["log_path"])
    if not path.exists():
        return {"status": "ok", "operation_id": operation_id, "lines": [], "message": "log ainda não criado"}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return {"status": "ok", "operation_id": operation_id, "line_count": len(lines), "lines": lines[-tail_lines:]}
