#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA Provisioner — Drift Audit
# =============================================================================
# Automated drift audit comparing declared state vs. actual state.
#
# Usage:
#   bash lib/drift_audit.sh P1   # Audit after Phase P1
#   bash lib/drift_audit.sh P3   # Audit after Phase P3
#   bash lib/drift_audit.sh ALL  # Full audit (Phase P5 / graduation)
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

PHASE="${1:-ALL}"
ERRORS=0

# Expected skills dynamically loaded from common.sh

audit_check() {
  local id="$1"
  local expected="$2"
  local actual="$3"

  if [ "$expected" = "$actual" ]; then
    printf "| %-20s | %-12s | %-12s | ${GREEN}✅ PASS${NC} |\n" "$id" "$expected" "$actual"
  else
    printf "| %-20s | %-12s | %-12s | ${RED}❌ FAIL${NC} |\n" "$id" "$expected" "$actual"
    ERRORS=$((ERRORS + 1))
  fi
}

run_audit() {
  local phase="$1"
  local expected_skills="${EXPECTED_SKILLS:-15}"

  step "Drift Audit — Phase $phase"
  echo ""
  printf "| %-20s | %-12s | %-12s | %-10s |\n" "Check" "Expected" "Actual" "Status"
  printf "|%-22s|%-14s|%-14s|%-12s|\n" "----------------------" "--------------" "--------------" "------------"

  # Check 1: Skills count
  local actual_skills=0
  if [ -d "$EXOCORTEX_SKILLS" ]; then
    actual_skills=$(find "$EXOCORTEX_SKILLS" -mindepth 1 -maxdepth 1 -type d | wc -l)
  fi
  audit_check "Skills count" "$expected_skills" "$actual_skills"

  # Check 2: Bundle sync
  local bundle_file="$HERMES_HOME/skill-bundles/exocortex-alpha.yaml"
  local bundle_count=0
  if [ -f "$bundle_file" ]; then
    bundle_count=$(grep "^  -" "$bundle_file" | wc -l)
  fi
  # Bundle has 15 core + browser-use optional marker = check against expected
  audit_check "Bundle entries" "$expected_skills" "$bundle_count"

  # Check 3: SOUL.md exists and has content
  local soul_status="missing"
  if [ -f "$HERMES_HOME/SOUL.md" ]; then
    local soul_lines
    soul_lines=$(wc -l < "$HERMES_HOME/SOUL.md")
    if [ "$soul_lines" -gt 5 ]; then
      soul_status="present"
    else
      soul_status="skeleton"
    fi
  fi
  local expected_soul="present"
  [ "$phase" = "P1" ] && expected_soul="present"  # After P1, SOUL should be populated
  audit_check "SOUL.md" "$expected_soul" "$soul_status"

  # Check 4: Acervo layers
  local acervo_layers=0
  for layer in macro global micro shared; do
    [ -d "$HERMES_HOME/acervo/$layer" ] && acervo_layers=$((acervo_layers + 1))
  done
  audit_check "Acervo layers" "$EXPECTED_ACERVO_LAYERS" "$acervo_layers"

  # Check 5: DESIGN.md exists (global tokens)
  local design_status="missing"
  [ -f "$HERMES_HOME/acervo/global/DESIGN.md" ] && design_status="present"
  audit_check "global/DESIGN.md" "present" "$design_status"

  # Check 6: Profiles (after P3)
  if [ "$phase" = "P3" ] || [ "$phase" = "P4" ] || [ "$phase" = "P5" ] || [ "$phase" = "ALL" ]; then
    local profile_count=0
    [ -d "$HERMES_HOME/profiles" ] && profile_count=$(find "$HERMES_HOME/profiles" -mindepth 1 -maxdepth 1 -type d | wc -l)
    audit_check "Profiles" "2" "$profile_count"
  fi

  echo ""
  if [ "$ERRORS" -eq 0 ]; then
    log "Drift Audit PASSED ✅"
  else
    fail "Drift Audit FAILED — $ERRORS issues found ❌"
  fi
}

run_audit "$PHASE"
exit "$ERRORS"
