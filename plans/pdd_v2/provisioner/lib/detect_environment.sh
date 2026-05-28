#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA Provisioner — Environment Detection
# =============================================================================
# Detects the current environment and outputs JSON for agent consumption.
#
# Usage:
#   bash lib/detect_environment.sh
#   bash lib/detect_environment.sh --quiet   # JSON only, no decoration
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

QUIET="${1:-}"

detect() {
  local os docker_available hermes_installed hermes_version
  local hermes_home existing_skills_count existing_provider existing_model

  # OS
  os="$(uname -s | tr '[:upper:]' '[:lower:]')"

  # Docker
  if has_command docker && docker info &>/dev/null; then
    docker_available="true"
  else
    docker_available="false"
  fi

  # Hermes
  if has_command hermes; then
    hermes_installed="true"
    hermes_version="$(hermes --version 2>/dev/null | head -1 | grep -oP 'v[\d.]+')" || hermes_version="unknown"
  else
    hermes_installed="false"
    hermes_version="none"
  fi

  # HERMES_HOME
  hermes_home="${HERMES_HOME}"

  # Existing skills
  if [ -d "$hermes_home/skills/exocortex" ]; then
    existing_skills_count="$(find "$hermes_home/skills/exocortex" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)"
  else
    existing_skills_count="0"
  fi

  # Existing LLM config
  if [ -f "$hermes_home/config.yaml" ]; then
    existing_provider="$(grep -A1 '^model:' "$hermes_home/config.yaml" 2>/dev/null | grep 'provider:' | awk '{print $2}')" || existing_provider="none"
    existing_model="$(grep -A1 '^model:' "$hermes_home/config.yaml" 2>/dev/null | grep 'default:' | awk '{print $2}')" || existing_model="none"
  else
    existing_provider="none"
    existing_model="none"
  fi

  # Python
  local python_version="none"
  if has_command python3; then
    python_version="$(python3 --version 2>/dev/null | awk '{print $2}')"
  fi

  # Artifacts
  local artifacts_present="false"
  if [ -d "$ARTIFACTS_DIR/skills" ] && [ -d "$ARTIFACTS_DIR/acervo" ]; then
    artifacts_present="true"
  fi

  # Output JSON
  cat <<EOF
{
  "os": "$os",
  "docker_available": $docker_available,
  "python_version": "$python_version",
  "hermes_installed": $hermes_installed,
  "hermes_version": "$hermes_version",
  "hermes_home": "$hermes_home",
  "existing_skills_count": $existing_skills_count,
  "existing_provider": "$existing_provider",
  "existing_model": "$existing_model",
  "artifacts_present": $artifacts_present
}
EOF
}

if [ "$QUIET" = "--quiet" ] || [ "$QUIET" = "-q" ]; then
  detect
else
  step "Detecting environment..."
  output=$(detect)
  echo "$output"

  # Human-readable summary
  echo ""
  os=$(echo "$output" | grep '"os"' | cut -d'"' -f4)
  hermes=$(echo "$output" | grep '"hermes_installed"' | grep -o 'true\|false')
  docker=$(echo "$output" | grep '"docker_available"' | grep -o 'true\|false')
  skills=$(echo "$output" | grep '"existing_skills_count"' | grep -oP '\d+')

  [ "$hermes" = "true" ] && log "Hermes instalado" || warn "Hermes não encontrado"
  [ "$docker" = "true" ] && log "Docker disponível" || info "Docker não disponível"
  info "Skills Exocórtex existentes: $skills"
fi
