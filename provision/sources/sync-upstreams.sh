#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCK_FILE="$SCRIPT_DIR/sources.lock.yaml"
WORKSPACE_DEFAULT="$SCRIPT_DIR/worktrees"
APPLY=0
ALLOW_CLONE=0
ALLOW_FETCH=0
WORKSPACE="$WORKSPACE_DEFAULT"
ONLY_SOURCE=""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
info() { echo -e "${CYAN}ℹ${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; exit 1; }

usage() {
  cat <<EOF
Uso:
  bash provision/sources/sync-upstreams.sh [opções]

Default: dry-run absoluto. Não clona, não faz fetch, não faz push, não faz merge.

Opções:
  --apply                 Permite mutação local quando combinada com flags explícitas.
  --clone-missing         Com --apply, clona localmente fontes ausentes.
  --fetch-existing        Com --apply, faz fetch local em clones já existentes.
  --workspace PATH        Define raiz local dos worktrees. Default: $WORKSPACE_DEFAULT
  --source NAME           Restringe a uma fonte (ex.: hermes-agent)
  -h, --help              Mostra esta ajuda.

Exemplos:
  bash provision/sources/sync-upstreams.sh
  bash provision/sources/sync-upstreams.sh --apply --clone-missing
  bash provision/sources/sync-upstreams.sh --apply --fetch-existing --source hermes-agent
EOF
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || fail "Comando obrigatório ausente: $1"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --apply)
      APPLY=1
      ;;
    --clone-missing)
      ALLOW_CLONE=1
      ;;
    --fetch-existing)
      ALLOW_FETCH=1
      ;;
    --workspace)
      shift
      [ "$#" -gt 0 ] || fail "--workspace exige um caminho"
      WORKSPACE="$1"
      ;;
    --source)
      shift
      [ "$#" -gt 0 ] || fail "--source exige um nome"
      ONLY_SOURCE="$1"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "Opção desconhecida: $1"
      ;;
  esac
  shift
done

[ -f "$LOCK_FILE" ] || fail "Arquivo lock não encontrado: $LOCK_FILE"
require_cmd git
require_cmd python3

if [ "$APPLY" -eq 0 ] && { [ "$ALLOW_CLONE" -eq 1 ] || [ "$ALLOW_FETCH" -eq 1 ]; }; then
  fail "Flags --clone-missing/--fetch-existing exigem --apply"
fi

if [ "$APPLY" -eq 1 ] && [ "$ALLOW_CLONE" -eq 0 ] && [ "$ALLOW_FETCH" -eq 0 ]; then
  fail "--apply sozinho não faz nada. Use também --clone-missing e/ou --fetch-existing"
fi

if [ "$APPLY" -eq 1 ]; then
  mkdir -p "$WORKSPACE"
fi

mapfile -t SOURCE_ROWS < <(
python3 - "$LOCK_FILE" <<'PY'
import sys
from pathlib import Path

lock_path = Path(sys.argv[1])
text = lock_path.read_text(encoding='utf-8').splitlines()

entries = []
current = None
section = None

for raw in text:
    line = raw.rstrip("\n")
    if not line.strip() or line.lstrip().startswith("#"):
        continue

    if line.startswith("sources:"):
        section = "sources"
        continue

    if section != "sources":
        continue

    if not line.startswith("  "):
        continue

    indent = len(line) - len(line.lstrip(" "))
    stripped = line.strip()

    if indent == 2 and stripped.endswith(":"):
        if current:
            entries.append(current)
        name = stripped[:-1]
        current = {
            "name": name,
            "upstream_git": "",
            "upstream_owner_repo": "",
            "controlled_ref": "",
            "license_name": "",
            "license_spdx": "",
            "commercial": "",
            "redirect": "",
        }
        continue

    if current is None:
        continue

    if indent == 4 and stripped.endswith(":"):
        section2 = stripped[:-1]
        current["__subsection__"] = section2
        continue

    if ":" not in stripped:
        continue

    key, value = stripped.split(":", 1)
    key = key.strip()
    value = value.strip().strip('"').strip("'")
    subsection = current.get("__subsection__", "")

    if subsection == "upstream":
        if key == "git":
            current["upstream_git"] = value
        elif key == "owner_repo":
            current["upstream_owner_repo"] = value
        elif key == "observed_redirect":
            current["redirect"] = value
    elif subsection == "controlled":
        if key == "ref":
            current["controlled_ref"] = value
    elif subsection == "license":
        if key == "name":
            current["license_name"] = value
        elif key == "spdx":
            current["license_spdx"] = value
        elif key == "commercial_use_requires_license":
            current["commercial"] = value

if current:
    entries.append(current)

for item in entries:
    fields = [
        item.get("name", ""),
        item.get("upstream_git", ""),
        item.get("upstream_owner_repo", ""),
        item.get("controlled_ref", ""),
        item.get("license_name", "") or item.get("license_spdx", ""),
        item.get("commercial", ""),
        item.get("redirect", ""),
    ]
    print("\t".join(fields))
PY
)

[ "${#SOURCE_ROWS[@]}" -gt 0 ] || fail "Nenhuma fonte encontrada em $LOCK_FILE"

info "Modo: $([ "$APPLY" -eq 1 ] && echo 'apply local controlado' || echo 'dry-run')"
info "Workspace local: $WORKSPACE"
info "Lock file: $LOCK_FILE"
warn "Este script nunca faz push, merge, rebase, tag ou qualquer mutação remota."

for row in "${SOURCE_ROWS[@]}"; do
  IFS=$'\t' read -r NAME UPSTREAM_GIT UPSTREAM_OWNER_REPO CONTROLLED_REF LICENSE_NAME COMMERCIAL REDIRECT <<< "$row"

  if [ -n "$ONLY_SOURCE" ] && [ "$NAME" != "$ONLY_SOURCE" ]; then
    continue
  fi

  [ -n "$NAME" ] || fail "Entrada inválida no lock file"
  [ -n "$UPSTREAM_GIT" ] || fail "Fonte $NAME sem upstream.git"
  [ -n "$CONTROLLED_REF" ] || fail "Fonte $NAME sem controlled.ref"

  if [ "$NAME" != "hermes-webui" ]; then
    case "$CONTROLLED_REF" in
      main|master|HEAD)
        fail "Fonte $NAME usa controlled.ref flutuante proibida: $CONTROLLED_REF"
        ;;
    esac

    if [[ ! "$CONTROLLED_REF" =~ ^[0-9a-f]{40}$ ]]; then
      fail "Fonte $NAME deve usar controlled.ref com commit SHA-1 completo de 40 caracteres: $CONTROLLED_REF"
    fi
  else
    if [[ ! "$CONTROLLED_REF" =~ ^([0-9a-f]{40}|master|main)$ ]]; then
      fail "Fonte $NAME deve usar controlled.ref com commit SHA-1 completo, master ou main: $CONTROLLED_REF"
    fi
  fi

  TARGET_DIR="$WORKSPACE/$NAME"

  echo
  info "Fonte: $NAME"
  echo "  upstream:  $UPSTREAM_OWNER_REPO"
  echo "  git:       $UPSTREAM_GIT"
  echo "  ref alvo:  $CONTROLLED_REF"
  echo "  licença:   $LICENSE_NAME"
  if [ -n "$REDIRECT" ]; then
    echo "  redirect:  $REDIRECT"
  fi
  if [ "$COMMERCIAL" = "true" ]; then
    warn "$NAME exige atenção de licença para uso comercial"
  fi

  if [ ! -d "$TARGET_DIR/.git" ]; then
    if [ "$APPLY" -eq 1 ] && [ "$ALLOW_CLONE" -eq 1 ]; then
      info "Clonando localmente em $TARGET_DIR"
      git clone "$UPSTREAM_GIT" "$TARGET_DIR"
      log "Clone local concluído para $NAME"
    else
      warn "Clone ausente: $TARGET_DIR"
      info "Dry-run: faria git clone $UPSTREAM_GIT $TARGET_DIR"
      continue
    fi
  else
    log "Clone local já existe: $TARGET_DIR"
  fi

  if [ "$APPLY" -eq 1 ] && [ "$ALLOW_FETCH" -eq 1 ]; then
    info "Fazendo fetch local em $TARGET_DIR"
    git -C "$TARGET_DIR" fetch --tags --prune origin
    log "Fetch local concluído para $NAME"
  else
    info "Dry-run: faria git -C $TARGET_DIR fetch --tags --prune origin"
  fi

  if [ "$APPLY" -eq 1 ]; then
    git -C "$TARGET_DIR" cat-file -e "${CONTROLLED_REF}^{commit}" \
      || fail "Ref controlada não encontrada no clone local de $NAME: $CONTROLLED_REF"
    log "Ref controlada presente localmente para $NAME"
  fi

done

log "Sincronização inspecionada com segurança. Nenhuma mutação remota foi executada."
