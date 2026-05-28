#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA — Docker Entrypoint
# =============================================================================
set -euo pipefail

export HERMES_HOME="${HERMES_HOME:-/opt/data}"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

log()  { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; }
step() { echo -e "\n${BOLD}▸ $1${NC}"; }
info() { echo -e "${CYAN}ℹ${NC} $1"; }

PROVISIONER_DIR="/workspace/provisioner"
ARTIFACTS_DIR="/workspace/artifacts"

echo ""
echo -e "${BOLD}  Exocórtex.IA — Docker Provisioner${NC}"
echo -e "  HERMES_HOME=$HERMES_HOME"
echo ""

# ─── Step 1: Inject credentials ────────────────────────────────────────
step "Credentials..."

if [ -f /opt/secrets/.env ]; then
  cp /opt/secrets/.env "$HERMES_HOME/.env" 2>/dev/null || true
  log "Credentials from mounted secrets"
fi

# Accept env vars directly
for var in OPENROUTER_API_KEY ANTHROPIC_API_KEY OPENAI_API_KEY; do
  if [ -n "${!var:-}" ]; then
    mkdir -p "$HERMES_HOME"
    echo "${var}=${!var}" >> "$HERMES_HOME/.env"
    log "$var injected from environment"
  fi
done

# ─── Step 2: Golden image ──────────────────────────────────────────────
step "Golden image..."

if [ ! -d "$ARTIFACTS_DIR/skills" ]; then
  fail "Artifacts not found at $ARTIFACTS_DIR"
  exit 1
fi

mkdir -p "$HERMES_HOME/skills/exocortex"
cp -r "$ARTIFACTS_DIR/skills/"* "$HERMES_HOME/skills/exocortex/"
log "Skills: $(find "$HERMES_HOME/skills/exocortex" -mindepth 1 -maxdepth 1 -type d | wc -l)"

mkdir -p "$HERMES_HOME/acervo"/{macro/assets,global,micro/_template,shared/cross-refs}
cp -r "$ARTIFACTS_DIR/acervo/"* "$HERMES_HOME/acervo/"
log "Acervo (4 layers)"

if [ -d "$ARTIFACTS_DIR/profiles" ]; then
  mkdir -p "$HERMES_HOME/profiles"
  cp -r "$ARTIFACTS_DIR/profiles/"* "$HERMES_HOME/profiles/"
  log "Profiles"
fi

if [ -d "$ARTIFACTS_DIR/skill-bundles" ]; then
  mkdir -p "$HERMES_HOME/skill-bundles"
  cp "$ARTIFACTS_DIR/skill-bundles/"*.yaml "$HERMES_HOME/skill-bundles/"
  log "Bundle"
fi

if [ -f "$ARTIFACTS_DIR/SOUL_SEED.md" ]; then
  cp "$ARTIFACTS_DIR/SOUL_SEED.md" "$HERMES_HOME/SOUL.md"
  log "SOUL.md"
fi

# ─── Step 3: Verify ───────────────────────────────────────────────────
step "Verification..."
if [ -f "$PROVISIONER_DIR/lib/verify.sh" ]; then
  HERMES_HOME="$HERMES_HOME" bash "$PROVISIONER_DIR/lib/verify.sh" --post-provision || true
fi

# ─── Step 4: PDD (if AUTORUN) ────────────────────────────────────────
if [ "${AUTORUN:-false}" = "true" ]; then
  step "Auto-running PDD prompts..."
  INSTALL_DIR="$PROVISIONER_DIR"
  ARTIFACTS_DIR="$ARTIFACTS_DIR"

  # Source the local installer for run_pdd
  WITH_PDD=true
  PDD_PHASE="${PDD_PHASE:-}"
  DRY_RUN=false
  VERBOSE=false

  mkdir -p "$PROVISIONER_DIR/state"
  local_phases=("P1" "P2" "P3" "P4" "P5")

  for phase in "${local_phases[@]}"; do
    if [ -n "$PDD_PHASE" ] && [[ "$phase" > "$PDD_PHASE" ]]; then
      break
    fi
    if [ -f "$PROVISIONER_DIR/state/${phase}.done" ]; then
      info "Phase $phase already done. Skipping."
      continue
    fi

    step "PDD Phase $phase..."
    local context=""
    if [ -f "$PROVISIONER_DIR/prompts/_MASTER_CONTEXT.md" ]; then
      context=$(cat "$PROVISIONER_DIR/prompts/_MASTER_CONTEXT.md")
    fi

    local first=true
    for pf in $(ls -v "$PROVISIONER_DIR/prompts/${phase}_"*.md 2>/dev/null); do
      info "Executing $(basename "$pf")..."
      local clean
      clean=$(sed '/^---$/,/^---$/d' "$pf")
      if [ "$first" = true ] && [ -n "$context" ]; then
        hermes chat -q "${context}"$'\n\n'"${clean}" -c --quiet 2>&1 || true
        first=false
      else
        hermes chat -q "$clean" -c --quiet 2>&1 || true
      fi
    done

    touch "$PROVISIONER_DIR/state/${phase}.done"
    log "Phase $phase complete"
  done
else
  step "Interactive mode. Container ready."
  info "docker exec -it exocortex-provisioner hermes chat"
fi

# Keep container alive
exec tail -f /dev/null
