#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA Provisioner — Docker Entrypoint
# =============================================================================
# Entry point for the Docker provisioning container.
# Handles credential injection, golden image copy, and optional auto-run.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROVISIONER_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

source "$PROVISIONER_DIR/lib/common.sh"

# Override HERMES_HOME for Docker
export HERMES_HOME="${HERMES_HOME:-/opt/data}"

step "Exocórtex.IA Docker Provisioner"
info "HERMES_HOME=$HERMES_HOME"

# ─── Step 1: Inject credentials ────────────────────────────────────────
if [ -f /opt/secrets/.env ]; then
  log "Copying credentials from mounted secrets"
  cp /opt/secrets/.env "$HERMES_HOME/.env" 2>/dev/null || true
fi

# Also accept env vars directly
if [ -n "${OPENROUTER_API_KEY:-}" ]; then
  echo "OPENROUTER_API_KEY=$OPENROUTER_API_KEY" >> "$HERMES_HOME/.env"
  log "OpenRouter API key injected from environment"
fi

if [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  echo "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY" >> "$HERMES_HOME/.env"
  log "Anthropic API key injected from environment"
fi

# ─── Step 2: Provision golden image ────────────────────────────────────
step "Provisioning golden image..."

ARTIFACTS="/workspace/plans/pdd_v2/artifacts"

if [ ! -d "$ARTIFACTS" ]; then
  fail "Artifacts directory not found at $ARTIFACTS"
  fail "Make sure the repository is mounted at /workspace"
  exit 1
fi

# Skills
mkdir -p "$HERMES_HOME/skills/exocortex"
cp -r "$ARTIFACTS/skills/"* "$HERMES_HOME/skills/exocortex/"
log "Skills copied ($(find "$HERMES_HOME/skills/exocortex" -mindepth 1 -maxdepth 1 -type d | wc -l) skills)"

# Acervo
mkdir -p "$HERMES_HOME/acervo/"{macro,global,micro/_template,shared/cross-refs}
cp -r "$ARTIFACTS/acervo/"* "$HERMES_HOME/acervo/"
log "Acervo copied (4 layers)"

# Profiles
mkdir -p "$HERMES_HOME/profiles"
cp -r "$ARTIFACTS/profiles/"* "$HERMES_HOME/profiles/"
log "Profiles copied"

# Bundle
mkdir -p "$HERMES_HOME/skill-bundles"
cp "$ARTIFACTS/skill-bundles/"*.yaml "$HERMES_HOME/skill-bundles/"
log "Bundle copied"

# Identity
cp "$ARTIFACTS/SOUL_SEED.md" "$HERMES_HOME/SOUL.md"
log "SOUL_SEED.md → SOUL.md"

# ─── Step 3: Verify ───────────────────────────────────────────────────
step "Verifying provision..."
bash "$PROVISIONER_DIR/lib/verify.sh" --post-provision

# ─── Step 4: Auto-run or interactive ──────────────────────────────────
if [ "${AUTORUN:-false}" = "true" ]; then
  step "Auto-run mode: executing PDD via RUNBOOK..."
  info "The RUNBOOK will be read by the orchestrating agent externally."
  info "Container is ready. Use 'docker exec' to send prompts."
else
  step "Interactive mode. Container is ready."
  info "To provision manually, use:"
  info "  docker exec -it exocortex-provisioner hermes chat --skills exocortex-alpha"
  info ""
  info "To execute PDD via orchestrator:"
  info "  See RUNBOOK.md Phase 5 for prompt sequence."
fi

# Keep container alive
exec tail -f /dev/null
