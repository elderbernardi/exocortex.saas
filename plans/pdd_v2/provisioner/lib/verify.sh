#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA Provisioner — Structural Verification
# =============================================================================
# Verifies the structural integrity of artifacts or a provisioned HERMES_HOME.
#
# Usage:
#   bash lib/verify.sh --pre-provision    # Check artifacts/ before copying
#   bash lib/verify.sh --post-provision   # Check HERMES_HOME after copying
#   bash lib/verify.sh --json             # Output as JSON (for agent parsing)
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

MODE="${1:---post-provision}"
FORMAT="${2:-text}"
ERRORS=0
CHECKS=0

check() {
  local description="$1"
  local condition="$2"
  CHECKS=$((CHECKS + 1))

  if eval "$condition"; then
    [ "$FORMAT" != "--json" ] && log "$description"
    return 0
  else
    [ "$FORMAT" != "--json" ] && fail "$description"
    ERRORS=$((ERRORS + 1))
    return 1
  fi
}

count_dirs() {
  find "$1" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l
}

count_files() {
  find "$1" -type f 2>/dev/null | wc -l
}

# =============================================================================
# Pre-provision: verify artifacts/ is complete
# =============================================================================
pre_provision() {
  step "Verifying artifacts (pre-provision)"

  local base="$ARTIFACTS_DIR"

  check "artifacts/ directory exists" "[ -d '$base' ]"
  check "skills/ directory exists" "[ -d '$base/skills' ]"
  check "acervo/ directory exists" "[ -d '$base/acervo' ]"
  check "profiles/ directory exists" "[ -d '$base/profiles' ]"
  check "skill-bundles/ directory exists" "[ -d '$base/skill-bundles' ]"
  check "SOUL_SEED.md exists" "[ -f '$base/SOUL_SEED.md' ]"
  check "setup.sh exists" "[ -f '$base/setup.sh' ]"

  # Skills count
  local skill_count
  skill_count=$(count_dirs "$base/skills")
  check "Skills count = $EXPECTED_SKILLS (found: $skill_count)" "[ '$skill_count' -eq '$EXPECTED_SKILLS' ]"

  # Each skill has SKILL.md
  local missing_skillmd=0
  for skill_dir in "$base/skills"/*/; do
    local name
    name=$(basename "$skill_dir")
    if [ ! -f "$skill_dir/SKILL.md" ]; then
      [ "$FORMAT" != "--json" ] && fail "  $name/ missing SKILL.md"
      missing_skillmd=$((missing_skillmd + 1))
    fi
  done
  check "All skills have SKILL.md" "[ '$missing_skillmd' -eq 0 ]"

  # Acervo layers
  check "acervo/macro/ exists" "[ -d '$base/acervo/macro' ]"
  check "acervo/global/ exists" "[ -d '$base/acervo/global' ]"
  check "acervo/micro/ exists" "[ -d '$base/acervo/micro' ]"
  check "acervo/shared/ exists" "[ -d '$base/acervo/shared' ]"

  # Key files
  check "global/DESIGN.md exists" "[ -f '$base/acervo/global/DESIGN.md' ]"
  check "global/index.md exists" "[ -f '$base/acervo/global/index.md' ]"
  check "exocortex-alpha.yaml exists" "[ -f '$base/skill-bundles/exocortex-alpha.yaml' ]"

  # Profiles
  check "profiles/exec exists" "[ -d '$base/profiles/exec' ]"
  check "profiles/evol exists" "[ -d '$base/profiles/evol' ]"
}

# =============================================================================
# Post-provision: verify HERMES_HOME was correctly populated
# =============================================================================
post_provision() {
  step "Verifying HERMES_HOME (post-provision)"

  local base="$HERMES_HOME"

  check "HERMES_HOME exists" "[ -d '$base' ]"
  check "skills/exocortex/ exists" "[ -d '$base/skills/exocortex' ]"
  check "acervo/ exists" "[ -d '$base/acervo' ]"

  # Skills count
  local skill_count
  skill_count=$(count_dirs "$base/skills/exocortex")
  check "Skills count = $EXPECTED_SKILLS (found: $skill_count)" "[ '$skill_count' -eq '$EXPECTED_SKILLS' ]"

  # Acervo layers
  check "acervo/macro/ exists" "[ -d '$base/acervo/macro' ]"
  check "acervo/global/ exists" "[ -d '$base/acervo/global' ]"
  check "acervo/micro/ exists" "[ -d '$base/acervo/micro' ]"
  check "acervo/shared/ exists" "[ -d '$base/acervo/shared' ]"

  # Identity
  check "SOUL.md exists" "[ -f '$base/SOUL.md' ]"

  # Bundle
  check "exocortex-alpha.yaml installed" "[ -f '$base/skill-bundles/exocortex-alpha.yaml' ]"

  # Profiles
  local profile_count
  profile_count=$(count_dirs "$base/profiles" 2>/dev/null || echo 0)
  check "Profiles installed (found: $profile_count)" "[ '$profile_count' -ge 2 ]"

  # Key acervo files
  check "global/DESIGN.md installed" "[ -f '$base/acervo/global/DESIGN.md' ]"

  # Hermes CLI
  check "hermes CLI available" "has_command hermes"
}

# =============================================================================
# Main
# =============================================================================
case "$MODE" in
  --pre-provision|-pre)
    pre_provision
    ;;
  --post-provision|-post)
    post_provision
    ;;
  *)
    echo "Usage: verify.sh [--pre-provision|--post-provision] [--json]"
    exit 1
    ;;
esac

# Summary
echo ""
if [ "$ERRORS" -eq 0 ]; then
  log "All $CHECKS checks passed ✅"
else
  fail "$ERRORS/$CHECKS checks failed ❌"
fi

exit "$ERRORS"
