#!/usr/bin/env bash
# =============================================================================
#  Exocórtex.IA — Autonomous Installer v3.0.0
#
#  curl -fsSL https://raw.githubusercontent.com/elderbernardi/exocortex.saas/main/install-exocortex.sh | bash
#  curl -fsSL ... | bash -s -- --mode docker --api-key sk-or-xxx
# =============================================================================
set -euo pipefail

readonly INSTALLER_VERSION="3.0.0"
readonly REPO="elderbernardi/exocortex.saas"
readonly BRANCH="main"
readonly TARBALL_URL="https://github.com/$REPO/archive/refs/heads/$BRANCH.tar.gz"
readonly PROVISIONER_REL="plans/pdd_v2/provisioner"

# ─── Defaults ────────────────────────────────────────────────────────────────
MODE="local"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
API_KEY=""
PROVIDER=""
SKIP_INSTALL=false
SKIP_AUTH=false
SKIP_GOLDEN_IMAGE=false
WITH_PDD=false
PDD_PHASE=""
NON_INTERACTIVE=false
VERBOSE=false
DRY_RUN=false
FORCE=false
NO_COLOR=false
DOCKER_IMAGE="exocortex-provisioner:latest"
DOCKER_DATA="exocortex-data"
DOCKER_DETACH=false
REPO_DIR=""

# ─── Colors ──────────────────────────────────────────────────────────────────
setup_colors() {
  if [ "$NO_COLOR" = true ] || [ ! -t 1 ]; then
    RED=''; GREEN=''; YELLOW=''; CYAN=''; BOLD=''; DIM=''; NC=''
  else
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
    CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'
  fi
}

log()  { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; }
step() { echo -e "\n${BOLD}▸ $1${NC}"; }
info() { echo -e "${CYAN}ℹ${NC} $1"; }
debug() { [ "$VERBOSE" = true ] && echo -e "${DIM}  [debug] $1${NC}" || true; }

die() { fail "$1"; exit "${2:-1}"; }

# ─── Usage ───────────────────────────────────────────────────────────────────
show_help() {
  cat <<'EOF'
Exocórtex.IA — Autonomous Installer v3.0.0

Usage: install-exocortex.sh [OPTIONS]

Installation Mode:
  --mode <local|docker>       Installation mode (default: local)

Credentials:
  --provider <name>           LLM provider: openrouter, anthropic, openai, nous
  --api-key <KEY>             API key for the LLM provider
  --skip-auth                 Skip LLM authentication setup

Flow Control:
  --with-pdd                  Execute PDD prompts after golden image
  --phase <P1..P5>            Run PDD only up to this phase
  --skip-install              Don't install Hermes (assume installed)
  --skip-golden-image         Don't copy golden image (PDD only)

Docker Options:
  --docker-image <name>       Docker image name (default: exocortex-provisioner:latest)
  --docker-data <name>        Docker volume name (default: exocortex-data)
  --docker-detach             Run container in background

Paths:
  --hermes-home <path>        Hermes home directory (default: ~/.hermes)
  --repo-dir <path>           Local repo path (auto-detected or downloaded)

Behavior:
  --non-interactive           No prompts, use defaults for everything
  --verbose                   Detailed output
  --dry-run                   Show what would be done without executing
  --force                     Overwrite without backup
  --no-color                  Disable colored output
  --version                   Show version and exit
  --help                      Show this help

Examples:
  # Simple local install (golden image only)
  curl -fsSL .../install-exocortex.sh | bash

  # Remote with API key, no prompts
  curl -fsSL .../install-exocortex.sh | bash -s -- --api-key sk-or-xxx --non-interactive

  # Docker mode
  bash install-exocortex.sh --mode docker --api-key sk-or-xxx

  # Full PDD execution
  bash install-exocortex.sh --with-pdd --api-key sk-or-xxx

  # Dry run
  bash install-exocortex.sh --dry-run --verbose
EOF
  exit 0
}

# ─── Argument Parser ─────────────────────────────────────────────────────────
parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --mode)           MODE="$2"; shift 2 ;;
      --provider)       PROVIDER="$2"; shift 2 ;;
      --api-key)        API_KEY="$2"; shift 2 ;;
      --skip-auth)      SKIP_AUTH=true; shift ;;
      --with-pdd)       WITH_PDD=true; shift ;;
      --phase)          PDD_PHASE="$2"; WITH_PDD=true; shift 2 ;;
      --skip-install)   SKIP_INSTALL=true; shift ;;
      --skip-golden-image) SKIP_GOLDEN_IMAGE=true; shift ;;
      --docker-image)   DOCKER_IMAGE="$2"; shift 2 ;;
      --docker-data)    DOCKER_DATA="$2"; shift 2 ;;
      --docker-detach)  DOCKER_DETACH=true; shift ;;
      --hermes-home)    HERMES_HOME="$2"; shift 2 ;;
      --repo-dir)       REPO_DIR="$2"; shift 2 ;;
      --non-interactive) NON_INTERACTIVE=true; shift ;;
      --verbose)        VERBOSE=true; shift ;;
      --dry-run)        DRY_RUN=true; shift ;;
      --force)          FORCE=true; shift ;;
      --no-color)       NO_COLOR=true; shift ;;
      --version)        echo "install-exocortex.sh v$INSTALLER_VERSION"; exit 0 ;;
      --help|-h)        show_help ;;
      *) die "Unknown option: $1. Use --help for usage." ;;
    esac
  done
}

# ─── Banner ──────────────────────────────────────────────────────────────────
show_banner() {
  echo ""
  echo -e "${BOLD}  ╔═══════════════════════════════════════╗${NC}"
  echo -e "${BOLD}  ║${NC}   ${CYAN}Exocórtex.IA${NC} — Installer v${INSTALLER_VERSION}     ${BOLD}║${NC}"
  echo -e "${BOLD}  ╚═══════════════════════════════════════╝${NC}"
  echo ""
  info "Mode: ${BOLD}$MODE${NC}"
  info "HERMES_HOME: $HERMES_HOME"
  [ -n "$API_KEY" ] && info "API Key: ${API_KEY:0:8}..." || true
  [ "$WITH_PDD" = true ] && info "PDD: enabled${PDD_PHASE:+ (up to $PDD_PHASE)}" || info "PDD: disabled (golden image only)"
  [ "$DRY_RUN" = true ] && warn "DRY RUN — no changes will be made"
  echo ""
}

# ─── Resolve Provisioner Directory ───────────────────────────────────────────
resolve_repo() {
  # 1. Explicit --repo-dir
  if [ -n "$REPO_DIR" ] && [ -d "$REPO_DIR/$PROVISIONER_REL" ]; then
    INSTALL_DIR="$REPO_DIR/$PROVISIONER_REL"
    ARTIFACTS_DIR="$REPO_DIR/plans/pdd_v2/artifacts"
    log "Using explicit repo: $REPO_DIR"
    return 0
  fi

  # 2. Current directory is repo
  if [ -d "$PWD/$PROVISIONER_REL" ]; then
    INSTALL_DIR="$PWD/$PROVISIONER_REL"
    ARTIFACTS_DIR="$PWD/plans/pdd_v2/artifacts"
    log "Using local repo: $PWD"
    return 0
  fi

  # 3. Download from GitHub
  step "Downloading Exocórtex from github.com/$REPO..."
  local tmpdir
  tmpdir=$(mktemp -d)
  trap "rm -rf '$tmpdir'" EXIT

  if [ "$DRY_RUN" = true ]; then
    info "[dry-run] Would download $TARBALL_URL"
    INSTALL_DIR="$tmpdir/provisioner"
    ARTIFACTS_DIR="$tmpdir/artifacts"
    mkdir -p "$INSTALL_DIR" "$ARTIFACTS_DIR"
    return 0
  fi

  curl -fsSL "$TARBALL_URL" -o "$tmpdir/repo.tar.gz"
  tar xzf "$tmpdir/repo.tar.gz" -C "$tmpdir"
  local extracted
  extracted=$(find "$tmpdir" -maxdepth 1 -type d -name "exocortex*" | head -1)

  [ -z "$extracted" ] && die "Failed to extract repo archive"

  INSTALL_DIR="$extracted/$PROVISIONER_REL"
  ARTIFACTS_DIR="$extracted/plans/pdd_v2/artifacts"

  [ -d "$INSTALL_DIR" ] || die "Provisioner not found in downloaded repo"
  log "Downloaded and extracted"
}

# ─── Main ────────────────────────────────────────────────────────────────────
main() {
  parse_args "$@"
  setup_colors
  show_banner

  # Validate mode
  case "$MODE" in
    local|docker) ;;
    *) die "Invalid mode: $MODE. Use 'local' or 'docker'." ;;
  esac

  # Resolve repo/provisioner location
  resolve_repo

  # Dispatch to mode-specific handler
  if [ "$MODE" = "docker" ]; then
    source "$INSTALL_DIR/lib/installer_docker.sh"
    run_docker_mode
  else
    source "$INSTALL_DIR/lib/installer_local.sh"
    run_local_mode
  fi
}

main "$@"
