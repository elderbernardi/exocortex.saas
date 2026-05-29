#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA — Local Installation Module
# =============================================================================
# Sourced by install-exocortex.sh. All variables inherited from parent.
# =============================================================================

# ─── Spinner & Progress Feedback ─────────────────────────────────────────────
# Background spinner with elapsed time. Keeps the user informed during
# long-running hermes chat calls that can take 30s+.
SPINNER_PID=""
SPINNER_FRAMES=("⠋" "⠙" "⠹" "⠸" "⠼" "⠴" "⠦" "⠧" "⠇" "⠏")

spinner_start() {
  local label="${1:-Processing}"
  local start_ts=$SECONDS
  (
    local i=0
    while true; do
      local elapsed=$(( SECONDS - start_ts ))
      local mins=$(( elapsed / 60 ))
      local secs=$(( elapsed % 60 ))
      local time_str
      if [ "$mins" -gt 0 ]; then
        time_str="${mins}m${secs}s"
      else
        time_str="${secs}s"
      fi
      printf '\r  %s %b %b(%s)%b ' \
        "${SPINNER_FRAMES[$((i % ${#SPINNER_FRAMES[@]}))]]}" \
        "${DIM}${label}${NC}" \
        "${DIM}" "$time_str" "${NC}"
      i=$((i + 1))
      sleep 0.12
    done
  ) &
  SPINNER_PID=$!
  disown "$SPINNER_PID" 2>/dev/null
}

spinner_stop() {
  if [ -n "$SPINNER_PID" ]; then
    kill "$SPINNER_PID" 2>/dev/null
    wait "$SPINNER_PID" 2>/dev/null || true
    SPINNER_PID=""
    printf '\r\033[K'  # clear spinner line
  fi
}

# Prints a compact progress bar: ████░░░░ 3/5
print_progress_bar() {
  local current="$1" total="$2" width=20
  local filled=$(( current * width / total ))
  local empty=$(( width - filled ))
  local bar=""
  for ((i=0; i<filled; i++)); do bar+="█"; done
  for ((i=0; i<empty; i++)); do bar+="░"; done
  printf '  %b%s%b %s/%s' "${CYAN}" "$bar" "${NC}" "$current" "$total"
}

# Formats a human-friendly prompt name from filename
# P1_001_bootstrap_self_test.md → bootstrap self test
friendly_prompt_name() {
  local name="$1"
  name="${name%.md}"                   # strip .md
  name="${name#P[0-9]_[0-9][0-9][0-9]_}"  # strip P1_001_
  echo "${name//_/ }"                  # underscores → spaces
}


# ─── Install Hermes Agent ────────────────────────────────────────────────────
install_hermes() {
  if [ "$SKIP_INSTALL" = true ]; then
    info "Hermes install skipped ${DIM}(--skip-install)${NC}"
    return 0
  fi

  if command -v hermes &>/dev/null; then
    local hermes_path
    hermes_path=$(command -v hermes)
    log "Hermes binary found: ${DIM}$hermes_path${NC}"
    hermes_health_check
    return 0
  fi

  step "Installing Hermes Agent..."
  info "Hermes is the AI agent runtime that powers Exocórtex."

  if [ "$DRY_RUN" = true ]; then
    info "[dry-run] Would install Hermes via official script"
    return 0
  fi

  # Try official install script first
  info "Trying official installer ${DIM}(NousResearch/hermes-agent)${NC}..."
  if curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash; then
    log "Hermes installed via official script"
  elif command -v pip3 &>/dev/null; then
    warn "Official script failed, trying pip3..."
    info "Running: ${DIM}pip3 install --user hermes-agent${NC}"
    pip3 install --user hermes-agent
  elif command -v pipx &>/dev/null; then
    warn "pip3 not available, trying pipx..."
    info "Running: ${DIM}pipx install hermes-agent${NC}"
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

  info "Running health check..."

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

  local ver_line
  ver_line=$(echo "$ver_output" | head -1)
  log "$ver_line"

  # Show extra details from version output
  echo "$ver_output" | tail -n +2 | while IFS= read -r line; do
    [ -n "$line" ] && echo -e "    ${DIM}$line${NC}"
  done

  # Test 2: hermes help must work (validates core modules load)
  if ! hermes --help &>/dev/null 2>&1; then
    warn "hermes --help failed — some modules may not be loaded"
  else
    log "Core modules loaded OK"
  fi
}

# ─── Configure LLM Auth ─────────────────────────────────────────────────────
configure_auth() {
  if [ "$SKIP_AUTH" = true ]; then
    info "Skipping auth (--skip-auth)"
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
    info "Configuring provided API credentials..."

    # Auto-detect provider from key prefix
    if [ -z "$PROVIDER" ]; then
      case "$API_KEY" in
        sk-or-*)  PROVIDER="openrouter" ;;
        sk-ant-*) PROVIDER="anthropic" ;;
        sk-*)     PROVIDER="openai" ;;
        *)        PROVIDER="openrouter" ;; # sensible default
      esac
      info "Auto-detected provider: ${BOLD}$PROVIDER${NC} ${DIM}(from key prefix)${NC}"
    else
      info "Provider: ${BOLD}$PROVIDER${NC}"
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
    log "Credentials saved: ${DIM}${env_var_name} → $HERMES_HOME/.env${NC}"
    return 0
  fi

  # Interactive mode — ask the user
  if [ "$NON_INTERACTIVE" = true ]; then
    warn "No API key provided and --non-interactive set. Skipping auth."
    warn "LLM features (PDD) will not work without credentials."
    return 0
  fi

  info "Starting interactive LLM configuration..."
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
    info "Skipping golden image (--skip-golden-image)"
    return 0
  fi

  info "Applying golden image artifacts to $HERMES_HOME..."

  # Validate artifacts exist
  if [ ! -d "$ARTIFACTS_DIR/skills" ] || [ ! -d "$ARTIFACTS_DIR/acervo" ]; then
    die "Artifacts directory incomplete: $ARTIFACTS_DIR"
  fi

  if [ "$DRY_RUN" = true ]; then
    local skill_count
    skill_count=$(find "$ARTIFACTS_DIR/skills" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)
    info "[dry-run] Would install $skill_count skills to $HERMES_HOME"
    return 0
  fi

  # Backup existing (unless --force)
  if [ -d "$HERMES_HOME/skills/exocortex" ] && [ "$FORCE" != true ]; then
    local ts
    ts=$(date +%Y%m%d%H%M%S)
    mv "$HERMES_HOME/skills/exocortex" "$HERMES_HOME/skills/exocortex_backup_$ts"
    info "Existing skills backed up to ${DIM}exocortex_backup_$ts${NC}"
  fi

  # Skills
  info "Installing skills..."
  mkdir -p "$HERMES_HOME/skills/exocortex"
  cp -r "$ARTIFACTS_DIR/skills/"* "$HERMES_HOME/skills/exocortex/"
  local sc
  sc=$(find "$HERMES_HOME/skills/exocortex" -mindepth 1 -maxdepth 1 -type d | wc -l)
  log "Skills installed: ${BOLD}$sc${NC}"

  # Acervo (4 layers)
  info "Installing Acervo memory layers..."
  mkdir -p "$HERMES_HOME/acervo"/{macro/assets,global,micro/_template,shared/cross-refs}
  cp -r "$ARTIFACTS_DIR/acervo/"* "$HERMES_HOME/acervo/"
  log "Acervo structure established"

  # Profiles
  if [ -d "$ARTIFACTS_DIR/profiles" ]; then
    info "Installing behavioral profiles..."
    mkdir -p "$HERMES_HOME/profiles"
    cp -r "$ARTIFACTS_DIR/profiles/"* "$HERMES_HOME/profiles/"
    local pc
    pc=$(find "$HERMES_HOME/profiles" -maxdepth 1 -type f -name '*.yaml' 2>/dev/null | wc -l)
    log "Profiles installed: ${BOLD}$pc${NC}"
  fi

  # Bundle
  if [ -d "$ARTIFACTS_DIR/skill-bundles" ]; then
    info "Installing skill bundles..."
    mkdir -p "$HERMES_HOME/skill-bundles"
    cp "$ARTIFACTS_DIR/skill-bundles/"*.yaml "$HERMES_HOME/skill-bundles/"
    log "Bundles installed"
  fi

  # Identity seed
  if [ -f "$ARTIFACTS_DIR/SOUL_SEED.md" ]; then
    info "Planting identity seed..."
    cp "$ARTIFACTS_DIR/SOUL_SEED.md" "$HERMES_HOME/SOUL.md"
    log "Identity seed planted"
  fi

  # File count summary
  local total_files
  total_files=$(find "$HERMES_HOME" -type f 2>/dev/null | wc -l)
  info "Golden image applied. ${DIM}Total files: $total_files${NC}"
}

# ─── Verify ──────────────────────────────────────────────────────────────────
verify_provision() {
  info "Verifying installation integrity..."

  if [ "$DRY_RUN" = true ]; then
    info "[dry-run] Would run post-provision verification"
    return 0
  fi

  if [ -f "$INSTALL_DIR/lib/verify.sh" ]; then
    info "Executing full verification suite..."
    if HERMES_HOME="$HERMES_HOME" bash "$INSTALL_DIR/lib/verify.sh" --post-provision 2>&1; then
      log "Full verification passed"
    else
      warn "Some verification checks failed (non-fatal)"
    fi
  else
    info "Running internal consistency checks..."
    local errors=0
    
    [ -d "$HERMES_HOME/skills/exocortex" ] && log "Skills directory: ${GREEN}OK${NC}" || { fail "Skills missing"; errors=$((errors+1)); }
    [ -d "$HERMES_HOME/acervo" ] && log "Acervo directory: ${GREEN}OK${NC}" || { fail "Acervo missing"; errors=$((errors+1)); }
    [ -f "$HERMES_HOME/SOUL.md" ] && log "Identity file: ${GREEN}OK${NC}" || { fail "SOUL.md missing"; errors=$((errors+1)); }

    if [ "$errors" -eq 0 ]; then
      log "All core checks passed"
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

  echo -e "  ${DIM}Each prompt sends instructions to Hermes — this takes a while.${NC}"
  echo -e "  ${DIM}Grab a ☕ — you'll see live progress below.${NC}"
  echo ""

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

  # Ensure spinner is killed on unexpected exit
  trap 'spinner_stop' EXIT

  local phases=("P1" "P2" "P3" "P4" "P5")
  local MAX_CONSECUTIVE_FAILURES=3
  local global_start=$SECONDS

  for phase in "${phases[@]}"; do
    # Phase gate
    if [ -n "$PDD_PHASE" ] && [[ "$phase" > "$PDD_PHASE" ]]; then
      debug "Stopping at phase $PDD_PHASE (current: $phase)"
      break
    fi

    # Idempotency
    if [ -f "$INSTALL_DIR/state/${phase}.done" ]; then
      log "Phase $phase already done. Skipping."
      continue
    fi

    # Count prompts for this phase upfront
    local prompt_files_arr=()
    while IFS= read -r f; do
      prompt_files_arr+=("$f")
    done < <(ls -v "$prompts_dir/${phase}_"*.md 2>/dev/null)
    local prompt_count=${#prompt_files_arr[@]}

    step "PDD Phase $phase  ${DIM}($prompt_count prompts)${NC}"

    if [ "$DRY_RUN" = true ]; then
      info "[dry-run] Would execute $prompt_count prompts for $phase"
      continue
    fi

    local context=""
    if [ -f "$prompts_dir/_MASTER_CONTEXT.md" ]; then
      context=$(cat "$prompts_dir/_MASTER_CONTEXT.md")
    fi

    local first=true
    local consecutive_failures=0
    local phase_failures=0
    local phase_idx=0
    local phase_start=$SECONDS

    for prompt_file in "${prompt_files_arr[@]}"; do
      local pname
      pname=$(basename "$prompt_file")
      phase_idx=$((phase_idx + 1))
      local friendly
      friendly=$(friendly_prompt_name "$pname")

      # Show which prompt is running with progress counter
      printf '\n  %b[%d/%d]%b %s\n' "${BOLD}" "$phase_idx" "$prompt_count" "${NC}" "$friendly"

      local clean_prompt
      clean_prompt=$(sed '/^---$/,/^---$/d' "$prompt_file")

      # Start spinner while hermes runs
      spinner_start "$friendly"

      local prompt_ok=false
      if [ "$first" = true ]; then
        # First prompt starts a NEW session (no -c flag).
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
        # Subsequent prompts continue the session.
        if hermes chat -q "$clean_prompt" -c --quiet 2>&1; then
          prompt_ok=true
        fi
      fi

      spinner_stop

      if [ "$prompt_ok" = true ]; then
        consecutive_failures=0
        echo -e "  ${GREEN}✓${NC} ${friendly} ${DIM}— done${NC}"
      else
        consecutive_failures=$((consecutive_failures + 1))
        phase_failures=$((phase_failures + 1))
        echo -e "  ${YELLOW}⚠${NC} ${friendly} ${DIM}— failed (${consecutive_failures} consecutive)${NC}"

        # Fail-fast: abort if hermes is systematically broken
        if [ "$consecutive_failures" -ge "$MAX_CONSECUTIVE_FAILURES" ]; then
          echo ""
          fail "$MAX_CONSECUTIVE_FAILURES consecutive prompt failures in $phase."
          fail "Hermes is likely not executing correctly."
          fail "Debug: hermes --version && hermes chat -q 'ping'"
          die "Aborting PDD. Fix Hermes and re-run with: --skip-install --skip-golden-image --with-pdd" 4
        fi
      fi
    done

    # Phase elapsed time
    local phase_elapsed=$(( SECONDS - phase_start ))
    local phase_mins=$(( phase_elapsed / 60 ))
    local phase_secs=$(( phase_elapsed % 60 ))
    local phase_time
    if [ "$phase_mins" -gt 0 ]; then
      phase_time="${phase_mins}m${phase_secs}s"
    else
      phase_time="${phase_secs}s"
    fi

    # Phase summary with progress bar
    echo ""
    local ok_count=$(( phase_idx - phase_failures ))
    print_progress_bar "$ok_count" "$phase_idx"
    echo ""

    if [ "$phase_failures" -gt 0 ]; then
      warn "Phase $phase: $phase_failures/$phase_idx prompts had issues ${DIM}(${phase_time})${NC}"
    fi

    # Drift audit
    if [ -f "$INSTALL_DIR/lib/drift_audit.sh" ]; then
      spinner_start "drift audit"
      if HERMES_HOME="$HERMES_HOME" bash "$INSTALL_DIR/lib/drift_audit.sh" "$phase" 2>&1; then
        spinner_stop
        touch "$INSTALL_DIR/state/${phase}.done"
        log "Phase $phase complete — drift audit passed ${DIM}(${phase_time})${NC}"
      else
        spinner_stop
        warn "Phase $phase — drift audit failed. Continuing anyway."
        touch "$INSTALL_DIR/state/${phase}.done"
      fi
    else
      touch "$INSTALL_DIR/state/${phase}.done"
      log "Phase $phase complete (${ok_count}/${phase_idx} OK) ${DIM}(${phase_time})${NC}"
    fi
  done

  # Total elapsed
  local total_elapsed=$(( SECONDS - global_start ))
  local total_mins=$(( total_elapsed / 60 ))
  local total_secs=$(( total_elapsed % 60 ))
  echo ""
  if [ "$total_mins" -gt 0 ]; then
    log "PDD complete in ${BOLD}${total_mins}m${total_secs}s${NC}"
  else
    log "PDD complete in ${BOLD}${total_secs}s${NC}"
  fi
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

# ─── Orchestrator ──────────────────────────────────────────────────────────
run_local_mode() {
  local install_start=$SECONDS

  step "Step 1/6 — Preflight checks"

  # Check basic prereqs
  info "Checking curl..."
  if ! command -v curl &>/dev/null; then
    die "curl is required. Install it first." 2
  fi
  log "curl ${DIM}$(curl --version 2>/dev/null | head -1 | cut -d' ' -f1-2)${NC}"

  info "Checking Python 3..."
  if ! command -v python3 &>/dev/null; then
    warn "Python 3 not found — Hermes Agent requires it"
    if [ "$SKIP_INSTALL" != true ]; then
      die "Install Python 3 first: sudo apt install python3" 2
    fi
  else
    log "python3 ${DIM}$(python3 --version 2>&1)${NC}"
  fi

  # Check optional tools
  if command -v git &>/dev/null; then
    log "git ${DIM}$(git --version 2>&1)${NC}"
  fi

  log "Preflight OK"

  step "Step 2/6 — Hermes Agent"
  install_hermes

  step "Step 3/6 — LLM Authentication"
  configure_auth

  step "Step 4/6 — Golden Image"
  apply_golden_image

  step "Step 5/6 — Verification"
  verify_provision

  # Step 6 is run_pdd (only if --with-pdd)
  if [ "$WITH_PDD" = true ]; then
    echo -e "\n${BOLD}▸ Step 6/6 — PDD Prompts${NC}"
  fi
  run_pdd

  # Total install time
  local total=$(( SECONDS - install_start ))
  local total_m=$(( total / 60 ))
  local total_s=$(( total % 60 ))
  echo ""
  if [ "$total_m" -gt 0 ]; then
    info "Total install time: ${BOLD}${total_m}m${total_s}s${NC}"
  else
    info "Total install time: ${BOLD}${total_s}s${NC}"
  fi

  show_summary
}
