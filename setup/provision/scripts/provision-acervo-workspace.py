#!/usr/bin/env python3
"""
Provisiona o Space "Acervo Cognitivo" no Hermes WebUI usando $ACERVO.
Idempotente — seguro rodar múltiplas vezes.

A variável canônica é $ACERVO (definida em common.sh, linha 58):
  ACERVO="${ACERVO:-$EXOCORTEX_HOME/acervo}"

Uso:
  python3 provision-acervo-workspace.py [--dry-run]

Saída:
  Código 0: success (já provisionado ou recém-criado)
  Código 1: ACERVO não definido (bloqueante)
  Código 2: WebUI não instalada (não-bloqueante — step segue)
"""

import json
import os
import sys
from pathlib import Path


# ── Helpers ──────────────────────────────────────────────────────────────

def log(msg):
    print(f"  {msg}")


def warn(msg):
    print(f"  ⚠ {msg}")


def ok(msg):
    print(f"  ✅ {msg}")


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    dry_run = "--dry-run" in sys.argv

    # 1. Resolve ACERVO
    acervo = os.environ.get("ACERVO", "").strip()
    if not acervo:
        exocortex_home = os.environ.get("EXOCORTEX_HOME", os.path.expanduser("~/exocortex"))
        acervo = os.path.join(exocortex_home, "acervo")
        log(f"ACERVO não definido; fallback: {acervo}")

    acervo_path = Path(acervo).expanduser().resolve()
    if not acervo_path.is_dir():
        warn(f"Acervo não encontrado em: {acervo_path}")
        warn("Space NÃO provisionado — diretório ausente.")
        return 0  # non-blocking: setup continua

    # 2. Resolve WebUI state dir
    hermes_home = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
    webui_state = os.environ.get(
        "HERMES_WEBUI_STATE_DIR",
        os.path.join(hermes_home, "webui"),
    )
    workspaces_file = Path(webui_state) / "workspaces.json"

    if not workspaces_file.parent.is_dir():
        log(f"WebUI state dir não encontrado: {workspaces_file.parent}")
        log("Space NÃO provisionado — WebUI não instalada ainda.")
        return 0  # non-blocking

    # 3. Read current workspaces
    workspaces = []
    if workspaces_file.exists():
        try:
            with open(workspaces_file) as f:
                workspaces = json.load(f)
        except (json.JSONDecodeError, IOError):
            workspaces = []

    # 4. Check if already provisioned (space entry)
    acervo_str = str(acervo_path)
    space_exists = False
    for ws in workspaces:
        if Path(ws.get("path", "")).expanduser().resolve() == acervo_path:
            space_exists = True
            ok(f"Space já provisionado: {ws.get('name')} → {acervo_str}")
            break

    # 5. Add the space if not present
    if not space_exists and not dry_run:
        new_space = {
            "name": "Acervo Cognitivo",
            "path": acervo_str,
        }
        workspaces.append(new_space)
        # Atomic write: temp file + rename
        tmp = str(workspaces_file) + ".tmp"
        with open(tmp, "w") as f:
            json.dump(workspaces, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp, str(workspaces_file))
        ok(f"Space provisionado: Acervo Cognitivo → {acervo_str}")
    elif not space_exists:
        log(f"DRY-RUN: adicionaria → {json.dumps({'name': 'Acervo Cognitivo', 'path': acervo_str})}")

    # 6. Ensure ACERVO is in WebUI .env (runtime needs it for artifact tools)
    env_path = Path(hermes_home) / "hermes-webui" / ".env"
    if env_path.exists():
        with open(env_path) as f:
            env_content = f.read()
        if "ACERVO=" not in env_content:
            if not dry_run:
                env_line = f"\n# Exocortex — Acervo Cognitivo canônico\nACERVO={acervo_str}\n"
                with open(env_path, "a") as f:
                    f.write(env_line)
                ok(f"WebUI .env: ACERVO={acervo_str}")
            else:
                log(f"DRY-RUN: adicionaria ACERVO={acervo_str} ao .env da WebUI")
        else:
            ok("WebUI .env: ACERVO já definido")

    return 0


if __name__ == "__main__":
    sys.exit(main())
