#!/usr/bin/env python3
"""Provision only the DataBrain event route; never print secrets or send messages.

Run as root: python3 scripts/provision_databrain_events.py --hermes-home /home/ubuntu/.hermes
Restart the user's gateway separately after reviewing and testing the provisioned config.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import secrets
import tempfile
from pathlib import Path
import yaml


PROMPT = """Evento operacional autenticado do DataBrain: {eventId}.
Consulte databrain_execution_status. O estado do evento é {daily.state}; pode haver observação mais recente.
Reconcilie o resultado observado e registre-o na resposta desta sessão operacional.
Confirme este evento com databrain_ack_event(event_id='{eventId}') somente após a consulta bem-sucedida.
Se a projeção estiver stale ou unavailable, não confirme; relate a indisponibilidade.
Um evento repetido não autoriza nova execução. Não iniciar pipelines, publicar dados, alterar gates,
alterar timers, fazer retries de publicação ou enviar mensagens a terceiros por causa deste evento.
Detalhes saneados: {__raw__}
"""


def with_route(config: dict, secret: str) -> dict:
    if len(secret) < 32:
        raise ValueError("HMAC secret too short")
    result = copy.deepcopy(config)
    hook = result.setdefault("platforms", {}).setdefault("webhook", {})
    extra = hook.setdefault("extra", {})
    if hook.get("enabled") and (extra.get("host", "127.0.0.1") != "127.0.0.1" or extra.get("port", 8644) != 8644):
        raise ValueError("Existing webhook listener must be reviewed before changing its binding")
    hook["enabled"] = True
    extra.update({"host": "127.0.0.1", "port": 8644})
    extra.setdefault("routes", {})["databrain-execution"] = {
        "secret": secret, "events": ["databrain.execution"], "deliver": "log", "prompt": PROMPT,
    }
    return result


def atomic_private(path: Path, content: str, uid: int, gid: int) -> None:
    fd, temporary = tempfile.mkstemp(prefix=".databrain-", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        os.fchown(fd, uid, gid)
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            out.write(content)
            out.flush()
            os.fsync(out.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hermes-home", type=Path, required=True)
    args = parser.parse_args()
    if os.getuid() != 0:
        raise SystemExit("Provisioning requires root")
    config_path = args.hermes_home / "config.yaml"
    metadata = config_path.lstat()
    if config_path.is_symlink() or metadata.st_mode & 0o022:
        raise SystemExit("Unsafe Hermes config permissions")
    config = yaml.safe_load(config_path.read_text())
    relay = Path("/etc/databrain/execution-control.json")
    if relay.is_symlink():
        raise SystemExit("Unsafe relay config")
    old = json.loads(relay.read_text()) if relay.exists() else {}
    secret = old.get("secret") or secrets.token_hex(32)
    updated = with_route(config, secret)
    backup = Path("/var/lib/databrain/execution-control/hermes-config.before.yaml")
    if not backup.exists():
        atomic_private(backup, config_path.read_text(), 0, 0)
    atomic_private(relay, json.dumps({"url": "http://127.0.0.1:8644/webhooks/databrain-execution", "secret": secret}) + "\n", 0, 0)
    atomic_private(config_path, yaml.safe_dump(updated, allow_unicode=True, sort_keys=False), metadata.st_uid, metadata.st_gid)
    print("DataBrain authenticated loopback route provisioned; gateway restart required")


if __name__ == "__main__":
    main()
