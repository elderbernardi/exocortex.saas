#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA — Local Installation Module
# =============================================================================
# Sourced by install-exocortex.sh. All variables inherited from parent.
# =============================================================================

# ─── Install Hermes Agent ────────────────────────────────────────────────────
install_hermes() {
  if [ "$SKIP_INSTALL" = true ]; then
    debug "Skipping Hermes install (--skip-install)"
    return 0
  fi

  if command -v hermes &>/dev/null; then
    log "Hermes binary found in PATH"
    hermes_health_check
    return 0
  fi

  step "Installing Hermes Agent..."

  if [ "$DRY_RUN" = true ]; then
    info "[dry-run] Would install Hermes via official script"
    return 0
  fi

  # Try official install script first
  if curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash; then
    log "Hermes installed via official script"
  elif command -v pip3 &>/dev/null; then
    warn "Official script failed, trying pip..."
    pip3 install --user hermes-agent
  elif command -v pipx &>/dev/null; then
    warn "Trying pipx..."
    pipx install hermes-agent
  else
    die "Failed to install Hermes. Install manually: pip install hermes-agent" 2
  fi

  # Verify binary exists
  if ! command -v hermes &>/dev/null; then
    die "Hermes installed but not found in PATH. Restart your shell and retry." 2
  fi

  hermes_health_check
}

# ─── Hermes Health Check ────────────────────────────────────────────────────
# Validates that hermes actually executes, not just that the binary exists.
# Catches: broken installs, missing python deps, corrupt virtualenvs, etc.
hermes_health_check() {
  if [ "$DRY_RUN" = true ]; then
    info "[dry-run] Would run hermes health check"
    return 0
  fi

  debug "Running hermes health check..."

  # Test 1: --version must exit 0 and produce output
  local ver_output
  if ! ver_output=$(hermes --version 2>&1); then
    fail "hermes --version failed"
    fail "Output: $ver_output"
    die "Hermes binary exists but does not execute. Check Python dependencies." 2
  fi

  if [ -z "$ver_output" ]; then
    die "hermes --version produced no output. Installation may be corrupt." 2
  fi

  log "Hermes $(echo "$ver_output" | head -1)"

  # Test 2: hermes help must work (validates core modules load)
  if ! hermes --help &>/dev/null 2>&1; then
    warn "hermes --help failed — some modules may not be loaded"
  fi

  debug "Health check passed"
}

# ─── Configure LLM Auth ─────────────────────────────────────────────────────
configure_auth() {
  if [ "$SKIP_AUTH" = true ]; then
    debug "Skipping auth (--skip-auth)"
    return 0
  fi

  # Check existing credentials
  if [ -f "$HERMES_HOME/config.yaml" ] || [ -f "$HERMES_HOME/.env" ]; then
    if [ -z "$API_KEY" ] && [ -z "$PROVIDER" ]; then
      log "Existing credentials found, using them"
      return 0
    fi
  fi

  # API key provided via CLI
  if [ -n "$API_KEY" ]; then
    step "Configuring LLM credentials..."

    # Auto-detect provider from key prefix
    if [ -z "$PROVIDER" ]; then
      case "$API_KEY" in
        sk-or-*)  PROVIDER="openrouter" ;;
        sk-ant-*) PROVIDER="anthropic" ;;
        sk-*)     PROVIDER="openai" ;;
        *)        PROVIDER="openrouter" ;; # sensible default
      esac
      debug "Auto-detected provider: $PROVIDER"
    fi

    if [ "$DRY_RUN" = true ]; then
      info "[dry-run] Would configure $PROVIDER with provided key"
      return 0
    fi

    # Write credentials
    mkdir -p "$HERMES_HOME"
    local env_var_name
    case "$PROVIDER" in
      openrouter) env_var_name="OPENROUTER_API_KEY" ;;
      anthropic)  env_var_name="ANTHROPIC_API_KEY" ;;
      openai)     env_var_name="OPENAI_API_KEY" ;;
      *)          env_var_name="API_KEY" ;;
    esac

    # Append to .env (don't overwrite)
    echo "${env_var_name}=${API_KEY}" >> "$HERMES_HOME/.env"
    log "Credentials configured for $PROVIDER"
    return 0
  fi

  # Interactive mode — ask the user
  if [ "$NON_INTERACTIVE" = true ]; then
    warn "No API key provided and --non-interactive set. Skipping auth."
    warn "LLM features (PDD) will not work without credentials."
    return 0
  fi

  step "LLM Authentication"
  echo ""
  echo "  How do you want to authenticate with the LLM?"
  echo "    1. OpenAI / ChatGPT (OAuth — opens browser)"
  echo "    2. Nous Research (OAuth — opens browser)"
  echo "    3. API Key (OpenRouter, Anthropic, etc.)"
  echo "    4. Skip — I'll configure later"
  echo ""
  read -rp "  Choice [4]: " auth_choice
  auth_choice="${auth_choice:-4}"

  case "$auth_choice" in
    1)
      hermes auth add codex-oauth 2>/dev/null || warn "OAuth setup may need manual completion"
      ;;
    2)
      hermes auth add nous --type oauth 2>/dev/null || warn "OAuth setup may need manual completion"
      ;;
    3)
      read -rp "  Paste your API key: " user_key
      if [ -n "$user_key" ]; then
        API_KEY="$user_key"
        configure_auth  # recurse with key now set
      fi
      ;;
    4)
      info "Auth skipped. Configure later with: hermes auth add <provider>"
      ;;
  esac
}

# ─── Apply Golden Image ─────────────────────────────────────────────────────
apply_golden_image() {
  if [ "$SKIP_GOLDEN_IMAGE" = true ]; then
    debug "Skipping golden image (--skip-golden-image)"
    return 0
  fi

  step "Applying golden image..."

  # Validate artifacts exist
  if [ ! -d "$ARTIFACTS_DIR/skills" ] || [ ! -d "$ARTIFACTS_DIR/acervo" ]; then
    die "Artifacts directory incomplete: $ARTIFACTS_DIR"
  fi

  if [ "$DRY_RUN" = true ]; then
    local skill_count
    skill_count=$(find "$ARTIFACTS_DIR/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)
    info "[dry-run] Would install $skill_count skills to $HERMES_HOME"
    info "[dry-run] Would install acervo (4 layers)"
    info "[dry-run] Would install profiles + bundles"
    return 0
  fi

  # Backup existing (unless --force)
  if [ -d "$HERMES_HOME/skills/exocortex" ] && [ "$FORCE" != true ]; then
    local ts
    ts=$(date +%Y%m%d%H%M%S)
    mv "$HERMES_HOME/skills/exocortex" "$HERMES_HOME/skills/exocortex_backup_$ts"
    info "Existing skills backed up to exocortex_backup_$ts"
  fi

  # Skills
  mkdir -p "$HERMES_HOME/skills/exocortex"
  cp -r "$ARTIFACTS_DIR/skills/"* "$HERMES_HOME/skills/exocortex/"
  local sc
  sc=$(find "$HERMES_HOME/skills/exocortex" -mindepth 1 -maxdepth 1 -type d | wc -l)
  log "Skills installed: $sc"

  # Acervo (4 layers)
  mkdir -p "$HERMES_HOME/acervo"/{macro/assets,global,micro/_template,shared/cross-refs}
  cp -r "$ARTIFACTS_DIR/acervo/"* "$HERMES_HOME/acervo/"
  log "Acervo installed (4 layers)"

  # Profiles
  if [ -d "$ARTIFACTS_DIR/profiles" ]; then
    mkdir -p "$HERMES_HOME/profiles"
    cp -r "$ARTIFACTS_DIR/profiles/"* "$HERMES_HOME/profiles/"
    log "Profiles installed"
  fi

  # Bundle
  if [ -d "$ARTIFACTS_DIR/skill-bundles" ]; then
    mkdir -p "$HERMES_HOME/skill-bundles"
    cp "$ARTIFACTS_DIR/skill-bundles/"*.yaml "$HERMES_HOME/skill-bundles/"
    log "Bundle installed"
  fi

  # Identity seed
  if [ -f "$ARTIFACTS_DIR/SOUL_SEED.md" ]; then
    cp "$ARTIFACTS_DIR/SOUL_SEED.md" "$HERMES_HOME/SOUL.md"
    log "SOUL.md installed from seed"
  fi
}

# ─── Verify ──────────────────────────────────────────────────────────────────
verify_provision() {
  step "Verifying installation..."

  if [ "$DRY_RUN" = true ]; then
    info "[dry-run] Would run post-provision verification"
    return 0
  fi

  if [ -f "$INSTALL_DIR/lib/verify.sh" ]; then
    if HERMES_HOME="$HERMES_HOME" bash "$INSTALL_DIR/lib/verify.sh" --post-provision 2>&1; then
      log "Verification passed"
    else
      warn "Some verification checks failed (non-fatal)"
    fi
  else
    # Inline minimal check
    local errors=0
    [ -d "$HERMES_HOME/skills/exocortex" ] || { fail "skills/exocortex/ missing"; errors=$((errors+1)); }
    [ -d "$HERMES_HOME/acervo" ]           || { fail "acervo/ missing"; errors=$((errors+1)); }
    [ -f "$HERMES_HOME/SOUL.md" ]          || { fail "SOUL.md missing"; errors=$((errors+1)); }

    if [ "$errors" -eq 0 ]; then
      log "Basic verification passed"
    else
      warn "$errors checks failed"
    fi
  fi
}

# ─── Execute PDD Prompts ────────────────────────────────────────────────────
run_pdd() {
  if [ "$WITH_PDD" != true ]; then
    return 0
  fi

  step "Executing PDD prompts..."

  # Gate 1: binary exists
  if ! command -v hermes &>/dev/null; then
    die "Hermes CLI not found. Cannot execute PDD prompts." 4
  fi

  # Gate 2: hermes actually works (not just present in PATH)
  if [ "$DRY_RUN" != true ]; then
    if ! hermes --version &>/dev/null 2>&1; then
      die "Hermes CLI exists but does not execute. Fix the installation before running PDD." 4
    fi
    debug "Hermes health check passed — ready for PDD"
  fi

  local prompts_dir="$INSTALL_DIR/prompts"
  if [ ! -d "$prompts_dir" ]; then
    die "Prompts directory not found: $prompts_dir" 4
  fi

  mkdir -p "$INSTALL_DIR/state"

  local phases=("P1" "P2" "P3" "P4" "P5")
  local MAX_CONSECUTIVE_FAILURES=3

  for phase in "${phases[@]}"; do
    # Phase gate
    if [ -n "$PDD_PHASE" ] && [[ "$phase" > "$PDD_PHASE" ]]; then
      debug "Stopping at phase $PDD_PHASE (current: $phase)"
      break
    fi

    # Idempotency
    if [ -f "$INSTALL_DIR/state/${phase}.done" ]; then
      info "Phase $phase already done. Skipping."
      continue
    fi

    step "PDD Phase $phase..."

    if [ "$DRY_RUN" = true ]; then
      local pc
      pc=$(find "$prompts_dir" -name "${phase}_*.md" -type f | wc -l)
      info "[dry-run] Would execute $pc prompts for $phase"
      continue
    fi

    local context=""
    if [ -f "$prompts_dir/_MASTER_CONTEXT.md" ]; then
      context=$(cat "$prompts_dir/_MASTER_CONTEXT.md")
    fi

    local first=true
    local consecutive_failures=0
    local phase_failures=0
    local phase_total=0

    for prompt_file in $(ls -v "$prompts_dir/${phase}_"*.md 2>/dev/null); do
      local pname
      pname=$(basename "$prompt_file")
      phase_total=$((phase_total + 1))
      info "Executing $pname..."

      local clean_prompt
      clean_prompt=$(sed '/^---$/,/^---$/d' "$prompt_file")

      local prompt_ok=false
      if [ "$first" = true ]; then
        # First prompt starts a NEW session (no -c flag).
        # -c tries to continue a previous session which doesn't exist yet.
        if [ -n "$context" ]; then
          if hermes chat -q "${context}"$'\n\n'"${clean_prompt}" --quiet 2>&1; then
            prompt_ok=true
          fi
        else
          if hermes chat -q "$clean_prompt" --quiet 2>&1; then
            prompt_ok=true
          fi
        fi
        first=false
      else
        # Subsequent prompts continue the session created by the first.
        if hermes chat -q "$clean_prompt" -c --quiet 2>&1; then
          prompt_ok=true
        fi
      fi

      if [ "$prompt_ok" = true ]; then
        consecutive_failures=0
        log "$pname OK"
      else
        consecutive_failures=$((consecutive_failures + 1))
        phase_failures=$((phase_failures + 1))
        warn "Prompt $pname failed ($consecutive_failures consecutive)"

        # Fail-fast: abort if hermes is systematically broken
        if [ "$consecutive_failures" -ge "$MAX_CONSECUTIVE_FAILURES" ]; then
          fail "$MAX_CONSECUTIVE_FAILURES consecutive prompt failures in $phase."
          fail "Hermes is likely not executing correctly."
          fail "Debug: hermes --version && hermes chat -q 'ping'"
          die "Aborting PDD. Fix Hermes and re-run with: --skip-install --skip-golden-image --with-pdd" 4
        fi
      fi
    done

    # Phase summary
    if [ "$phase_failures" -gt 0 ]; then
      warn "Phase $phase: $phase_failures/$phase_total prompts had issues"
    fi

    # Drift audit
    if [ -f "$INSTALL_DIR/lib/drift_audit.sh" ]; then
      if HERMES_HOME="$HERMES_HOME" bash "$INSTALL_DIR/lib/drift_audit.sh" "$phase" 2>&1; then
        touch "$INSTALL_DIR/state/${phase}.done"
        log "Phase $phase complete — drift audit passed"
      else
        warn "Phase $phase — drift audit failed. Continuing anyway."
        touch "$INSTALL_DIR/state/${phase}.done"
      fi
    else
      touch "$INSTALL_DIR/state/${phase}.done"
      log "Phase $phase complete ($((phase_total - phase_failures))/$phase_total OK)"
    fi
  done
}

# ─── Summary ─────────────────────────────────────────────────────────────────
show_summary() {
  local skill_count=0
  if [ -d "$HERMES_HOME/skills/exocortex" ] && [ "$DRY_RUN" != true ]; then
    skill_count=$(find "$HERMES_HOME/skills/exocortex" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)
  fi

  echo ""
  echo -e "${BOLD}  ┌─────────────────────────────────────────┐${NC}"
  echo -e "${BOLD}  │${NC}  ${GREEN}✅ Exocórtex.IA installed!${NC}                ${BOLD}│${NC}"
  echo -e "${BOLD}  │${NC}                                           ${BOLD}│${NC}"
  echo -e "${BOLD}  │${NC}  📦 Skills: $skill_count                              ${BOLD}│${NC}"
  echo -e "${BOLD}  │${NC}  📁 HERMES_HOME: ${DIM}$HERMES_HOME${NC}   ${BOLD}│${NC}"
  if [ "$WITH_PDD" = true ]; then
    echo -e "${BOLD}  │${NC}  🧠 PDD: executed                          ${BOLD}│${NC}"
  fi
  echo -e "${BOLD}  └─────────────────────────────────────────┘${NC}"
  echo ""
  echo "  Next steps:"
  echo "    hermes chat                    # Start chatting"
  echo "    hermes profile use exec        # Execution mode"
  echo "    hermes profile use evol        # Exploration mode"
  echo ""
}

# ─── Orchestrator ────────────────────────────────────────────────────────────
run_local_mode() {
  step "Preflight checks..."

  # Check basic prereqs
  if ! command -v curl &>/dev/null; then
    die "curl is required. Install it first." 2
  fi

  if ! command -v python3 &>/dev/null; then
    warn "Python 3 not found — Hermes Agent requires it"
    if [ "$SKIP_INSTALL" != true ]; then
      die "Install Python 3 first: sudo apt install python3" 2
    fi
  fi

  log "Preflight OK"

  install_hermes
  configure_auth
  apply_golden_image
  verify_provision
  run_pdd
  show_summary
}
