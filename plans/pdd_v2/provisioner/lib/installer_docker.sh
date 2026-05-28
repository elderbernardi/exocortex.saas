#!/usr/bin/env bash
# =============================================================================
# Exocórtex.IA — Docker Installation Module
# =============================================================================
# Sourced by install-exocortex.sh. All variables inherited from parent.
# =============================================================================

run_docker_mode() {
  step "Preflight checks (Docker mode)..."

  if ! command -v docker &>/dev/null; then
    die "Docker is required for --mode docker. Install: https://docs.docker.com/get-docker/" 2
  fi

  if ! docker info &>/dev/null 2>&1; then
    die "Docker daemon not running. Start it first." 2
  fi

  log "Docker available"

  # We need the repo locally for the Dockerfile and artifacts
  local docker_dir="$INSTALL_DIR/docker"
  if [ ! -d "$docker_dir" ]; then
    die "Docker directory not found: $docker_dir"
  fi

  # ─── Build image ──────────────────────────────────────────────────────────
  step "Building Docker image: $DOCKER_IMAGE..."

  if [ "$DRY_RUN" = true ]; then
    info "[dry-run] Would build $DOCKER_IMAGE from $docker_dir/Dockerfile"
    info "[dry-run] Would create volume $DOCKER_DATA"
    info "[dry-run] Would run container with golden image provisioning"
    show_docker_summary
    return 0
  fi

  if [ ! -f "$docker_dir/Dockerfile" ]; then
    die "Dockerfile not found at $docker_dir/Dockerfile"
  fi

  # Build from the repo root context to access artifacts
  local repo_root
  repo_root=$(cd "$INSTALL_DIR/../.." && pwd)

  docker build \
    -t "$DOCKER_IMAGE" \
    -f "$docker_dir/Dockerfile" \
    "$repo_root" \
    || die "Docker build failed"

  log "Image built: $DOCKER_IMAGE"

  # ─── Prepare env vars ─────────────────────────────────────────────────────
  local env_args=()
  env_args+=(-e "HERMES_HOME=/opt/data")

  if [ -n "$API_KEY" ]; then
    case "$API_KEY" in
      sk-or-*)  env_args+=(-e "OPENROUTER_API_KEY=$API_KEY") ;;
      sk-ant-*) env_args+=(-e "ANTHROPIC_API_KEY=$API_KEY") ;;
      sk-*)     env_args+=(-e "OPENAI_API_KEY=$API_KEY") ;;
      *)        env_args+=(-e "OPENROUTER_API_KEY=$API_KEY") ;;
    esac
  fi

  if [ "$WITH_PDD" = true ]; then
    env_args+=(-e "AUTORUN=true")
  fi

  if [ -n "$PDD_PHASE" ]; then
    env_args+=(-e "PDD_PHASE=$PDD_PHASE")
  fi

  # ─── Credential mounts ────────────────────────────────────────────────────
  local mount_args=()

  # Mount host .env if exists and no API key provided
  if [ -z "$API_KEY" ] && [ -f "$HOME/.hermes/.env" ]; then
    mount_args+=(-v "$HOME/.hermes/.env:/opt/secrets/.env:ro")
    info "Mounting host credentials from ~/.hermes/.env"
  fi

  # ─── Run container ────────────────────────────────────────────────────────
  step "Starting container..."

  local container_name="exocortex-provisioner"
  local run_args=()
  run_args+=(--name "$container_name")
  run_args+=(-v "$DOCKER_DATA:/opt/data")
  run_args+=("${mount_args[@]}")
  run_args+=("${env_args[@]}")

  # Remove existing container if present
  docker rm -f "$container_name" &>/dev/null || true

  if [ "$DOCKER_DETACH" = true ]; then
    docker run -d "${run_args[@]}" "$DOCKER_IMAGE"
    log "Container started in background: $container_name"
    echo ""
    info "Access: docker exec -it $container_name bash"
    info "Logs:   docker logs -f $container_name"
  else
    docker run -it "${run_args[@]}" "$DOCKER_IMAGE"
  fi

  show_docker_summary
}

show_docker_summary() {
  echo ""
  echo -e "${BOLD}  ┌─────────────────────────────────────────┐${NC}"
  echo -e "${BOLD}  │${NC}  ${GREEN}✅ Exocórtex.IA (Docker)${NC}                 ${BOLD}│${NC}"
  echo -e "${BOLD}  │${NC}                                           ${BOLD}│${NC}"
  echo -e "${BOLD}  │${NC}  📦 Image: $DOCKER_IMAGE    ${BOLD}│${NC}"
  echo -e "${BOLD}  │${NC}  💾 Data:  $DOCKER_DATA                   ${BOLD}│${NC}"
  echo -e "${BOLD}  └─────────────────────────────────────────┘${NC}"
  echo ""
  echo "  Commands:"
  echo "    docker exec -it exocortex-provisioner hermes chat"
  echo "    docker exec -it exocortex-provisioner hermes profile use exec"
  echo ""
}
