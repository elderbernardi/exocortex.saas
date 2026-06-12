#!/usr/bin/env bash
# =============================================================================
# Step 00: Hermes Compatibility Check
# =============================================================================
# Runs BEFORE any other setup step. Validates that the installed Hermes version
# is compatible with this Exocórtex release and that expected directory structure
# exists. Prevents silent breakage from Hermes updates.
#
# Exit codes:
#   0 = compatible
#   1 = incompatible (fatal)
#
# Standalone:
#   bash setup/step-00-hermes-compat.sh
# =============================================================================

# Standalone support
if [ "${_EXOCORTEX_COMMON_LOADED:-}" != "1" ]; then
  source "$(dirname "$0")/common.sh"
fi

# ─── Version bounds ─────────────────────────────────────────────────────────
# Update these when testing against new Hermes releases.
HERMES_MIN_VERSION="2026.4.8"
HERMES_MAX_TESTED="2026.4.16"

# ─── Helpers ────────────────────────────────────────────────────────────────

# Compare semver-like versions (YYYY.M.D format).
# Returns 0 if $1 >= $2, 1 otherwise.
version_gte() {
  local a b
  a=$(echo "$1" | tr '.' ' ')
  b=$(echo "$2" | tr '.' ' ')
  # Zero-pad to 3 fields
  set -- $a; local a1="${1:-0}" a2="${2:-0}" a3="${3:-0}"
  set -- $b; local b1="${1:-0}" b2="${2:-0}" b3="${3:-0}"

  if [ "$a1" -gt "$b1" ] 2>/dev/null; then return 0; fi
  if [ "$a1" -lt "$b1" ] 2>/dev/null; then return 1; fi
  if [ "$a2" -gt "$b2" ] 2>/dev/null; then return 0; fi
  if [ "$a2" -lt "$b2" ] 2>/dev/null; then return 1; fi
  if [ "$a3" -ge "$b3" ] 2>/dev/null; then return 0; fi
  return 1
}

# ─── Checks ─────────────────────────────────────────────────────────────────

check_hermes_version() {
  if ! command -v hermes >/dev/null 2>&1; then
    fail "hermes CLI not found in PATH. Install Hermes first."
  fi

  local raw_version version_output
  version_output=$(hermes --version 2>/dev/null || true)
  raw_version=${version_output%%$'\n'*}

  local version
  version=$(echo "$raw_version" | grep -oP '\d{4}\.\d+\.\d+' | head -1)

  if [ -z "$version" ]; then
    warn "Cannot parse Hermes version from: $raw_version"
    warn "Proceeding without version check — manual verification recommended."
    return 0
  fi

  # Check minimum
  if ! version_gte "$version" "$HERMES_MIN_VERSION"; then
    fail "Hermes $version is below minimum $HERMES_MIN_VERSION. Update Hermes first."
  fi

  # Check maximum tested (warn, don't fail)
  if ! version_gte "$HERMES_MAX_TESTED" "$version"; then
    warn "Hermes $version is newer than max tested $HERMES_MAX_TESTED."
    warn "Exocórtex may work but has not been tested with this version."
    warn "If issues arise, pin with: HERMES_PIN_VERSION=$HERMES_MAX_TESTED"
  fi

  log "Hermes version: $version (bounds: $HERMES_MIN_VERSION – $HERMES_MAX_TESTED)"
}

check_directory_structure() {
  local probes=(
    "$HERMES_HOME/skills"
    "$HERMES_HOME/memories"
  )

  for probe in "${probes[@]}"; do
    if [ ! -d "$probe" ]; then
      fail "Expected directory not found: $probe — Hermes may not be properly initialized."
    fi
  done

  # Profiles dir may not exist yet (created by step-05)
  if [ ! -d "$HERMES_HOME/profiles" ]; then
    warn "Profiles directory missing: $HERMES_HOME/profiles (will be created by step-05)"
    mkdir -p "$HERMES_HOME/profiles"
    log "Created profiles directory"
  fi

  log "Directory structure OK"
}

check_patch_targets() {
  # Probe files that step-06-hardening.sh patches
  local gapi="$HERMES_HOME/skills/productivity/google-workspace/scripts/google_api.py"

  if [ -f "$gapi" ]; then
    if grep -q "def drive_search" "$gapi" 2>/dev/null; then
      log "Patch target OK: google_api.py (drive_search found)"
    else
      warn "google_api.py structure changed — step-06 Drive patch may fail"
    fi
  else
    info "google_api.py not present — Drive patch will be skipped (harmless)"
  fi
}

# ─── Main ───────────────────────────────────────────────────────────────────

info "Checking Hermes compatibility..."

check_hermes_version
check_directory_structure
check_patch_targets

log "Hermes compatibility check passed"
