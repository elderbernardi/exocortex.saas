#!/usr/bin/env bash
# =============================================================================
# Exocórtex — Sync Repairs to Repository
# =============================================================================
# Protocolo de sincronização: instância Hermes → repositório exocortex.saas
# Lê repair manifests e aplica mudanças de volta ao repo fonte.
#
# Modo A: EXOCORTEX_REPO_PATH definido → branch + commit + (opcional) PR
# Modo B: Sem repo local → gerar patch + issue via Hermes headless
#
# Uso:
#   bash scripts/sync-repairs-to-repo.sh
#
# Variáveis de ambiente:
#   EXOCORTEX_REPO_PATH    Path do clone local do repo
#   EXOCORTEX_SYNC_AUTO_PR Se 1, cria PR via gh CLI
#   ACERVO                 Path do acervo na instância
#   HERMES_HOME            Path do Hermes home na instância
# =============================================================================

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Config
ACERVO="${ACERVO:-${EXOCORTEX_HOME:-$HOME/exocortex}/acervo}"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
REPO_PATH="${EXOCORTEX_REPO_PATH:-}"
AUTO_PR="${EXOCORTEX_SYNC_AUTO_PR:-0}"
HARNESS_MODEL="${EXOCORTEX_HARNESS_MODEL:-openai/gpt-5.4}"
# F-003: repair manifests/patches live outside the canonical Acervo (shared
# default + env var with test-helpers.sh).
EXOCORTEX_REPORT_DIR="${EXOCORTEX_REPORT_DIR:-$HERMES_HOME/reports/provisioning}"
REPAIRS_DIR="$EXOCORTEX_REPORT_DIR/repairs"
PATCHES_DIR="$EXOCORTEX_REPORT_DIR/patches"

_RED='\033[0;31m'
_GREEN='\033[0;32m'
_YELLOW='\033[1;33m'
_CYAN='\033[0;36m'
_GRAY='\033[0;90m'
_NC='\033[0m'

# =============================================================================
# Allowlist / Blocklist
# =============================================================================

# Paths que podem ser sincronizados (instância → repo)
ALLOWED_SYNC_PREFIXES=(
  "skills/excrtx/excrtx-"     # Skills
  "acervo/global/templates/"     # Templates seed
  "acervo/global/tools/"         # Harness tools
  "acervo/global/contracts/"     # Contracts
  "acervo/global/workflows/"     # Workflows
  "acervo/micro/_template/"      # Microverso template
  "profiles/"                    # Profiles
  "skill-bundles/"               # Bundles
)

# Paths que NUNCA devem ser sincronizados
BLOCKED_PATTERNS=(
  "macro/soul.md"
  "macro/valores.md"
  "macro/estilo.md"
  "SOUL.md"
  "memories/"
  "credential"
  "token"
  "secret"
  ".env"
  "__pycache__"
)

is_path_allowed() {
  local path="$1"

  # Check blocklist first
  for pattern in "${BLOCKED_PATTERNS[@]}"; do
    if [[ "$path" == *"$pattern"* ]]; then
      return 1
    fi
  done

  # Check allowlist
  for prefix in "${ALLOWED_SYNC_PREFIXES[@]}"; do
    if [[ "$path" == *"$prefix"* ]]; then
      return 0
    fi
  done

  return 1  # not in allowlist
}

# Map instance path to repo path
instance_to_repo_path() {
  local ipath="$1"

  # Skills: $HERMES_HOME/skills/excrtx/<skill>/ → skills/<skill>/
  if [[ "$ipath" == *"/skills/excrtx/"* ]]; then
    echo "skills/${ipath##*/skills/excrtx/}"
    return
  fi

  # Acervo: $ACERVO/<rest> → acervo/<rest>
  if [[ "$ipath" == "$ACERVO/"* ]]; then
    echo "acervo/${ipath#$ACERVO/}"
    return
  fi

  # Profiles: $HERMES_HOME/profiles/ → profiles/
  if [[ "$ipath" == *"/profiles/"* ]]; then
    echo "profiles/${ipath##*/profiles/}"
    return
  fi

  echo ""  # not mappable
}

# =============================================================================
# Main
# =============================================================================

echo ""
echo -e "${_CYAN}━━━ Sync de Reparos: Instância → Repositório ━━━${_NC}"
echo ""

# Find pending repair manifests
if [ ! -d "$REPAIRS_DIR" ]; then
  echo -e "  ${_GRAY}Sem diretório de repairs: $REPAIRS_DIR${_NC}"
  exit 0
fi

pending_manifests=()
for manifest in "$REPAIRS_DIR"/RPR-*.json; do
  [ -f "$manifest" ] || continue
  status=$(grep -o '"sync_status"[[:space:]]*:[[:space:]]*"[^"]*"' "$manifest" | grep -o '"[^"]*"$' | tr -d '"')
  if [ "$status" = "pending" ]; then
    pending_manifests+=("$manifest")
  fi
done

if [ ${#pending_manifests[@]} -eq 0 ]; then
  echo -e "  ${_GREEN}Nenhum reparo pendente de sync.${_NC}"
  exit 0
fi

echo -e "  Reparos pendentes: ${#pending_manifests[@]}"

# =============================================================================
# Modo A: Repo local disponível
# =============================================================================
if [ -n "$REPO_PATH" ] && [ -d "$REPO_PATH/.git" ]; then
  echo -e "  Modo: ${_GREEN}A (repo local)${_NC} — $REPO_PATH"
  echo ""

  # Ensure clean state
  if ! git -C "$REPO_PATH" diff --quiet 2>/dev/null; then
    echo -e "  ${_YELLOW}⚠ Repo tem mudanças não commitadas. Sync abortado.${_NC}"
    exit 1
  fi

  for manifest in "${pending_manifests[@]}"; do
    repair_id=$(grep -o '"repair_id"[[:space:]]*:[[:space:]]*"[^"]*"' "$manifest" | grep -o '"[^"]*"$' | tr -d '"')
    feature_id=$(grep -o '"feature_id"[[:space:]]*:[[:space:]]*"[^"]*"' "$manifest" | grep -o '"[^"]*"$' | tr -d '"')
    skill_name=$(grep -o '"skill_name"[[:space:]]*:[[:space:]]*"[^"]*"' "$manifest" | grep -o '"[^"]*"$' | tr -d '"')

    echo -e "  ${_CYAN}Processing: $repair_id ($feature_id)${_NC}"

    # Create branch
    branch_name="repair/${repair_id}"
    git -C "$REPO_PATH" checkout -b "$branch_name" main 2>/dev/null || \
    git -C "$REPO_PATH" checkout -b "$branch_name" 2>/dev/null || true

    # Diff and copy skill files
    instance_skill_dir="$HERMES_HOME/skills/excrtx/$skill_name"
    repo_skill_dir="$REPO_PATH/skills/$skill_name"

    if [ -d "$instance_skill_dir" ] && [ -d "$repo_skill_dir" ]; then
      changed_files=0
      while IFS= read -r file; do
        rel_path="${file#$instance_skill_dir/}"
        repo_file="$repo_skill_dir/$rel_path"

        # Check allowlist
        if ! is_path_allowed "skills/excrtx/$skill_name/$rel_path"; then
          echo -e "    ${_GRAY}Skip (blocklist): $rel_path${_NC}"
          continue
        fi

        # Diff
        if [ -f "$repo_file" ]; then
          if ! diff -q "$file" "$repo_file" >/dev/null 2>&1; then
            local diff_lines
            diff_lines=$(diff -u "$repo_file" "$file" | wc -l)
            if [ "$diff_lines" -gt 200 ]; then
              echo -e "    ${_YELLOW}⚠ Diff muito grande ($diff_lines linhas): $rel_path — escalar para review${_NC}"
              continue
            fi
            cp "$file" "$repo_file"
            git -C "$REPO_PATH" add "skills/$skill_name/$rel_path"
            changed_files=$((changed_files + 1))
            echo -e "    ${_GREEN}✓${_NC} Atualizado: $rel_path"
          fi
        else
          # New file
          mkdir -p "$(dirname "$repo_file")"
          cp "$file" "$repo_file"
          git -C "$REPO_PATH" add "skills/$skill_name/$rel_path"
          changed_files=$((changed_files + 1))
          echo -e "    ${_GREEN}+${_NC} Novo: $rel_path"
        fi
      done < <(find "$instance_skill_dir" -type f)

      if [ $changed_files -gt 0 ]; then
        # Commit
        local error_desc
        error_desc=$(grep -o '"error"[[:space:]]*:[[:space:]]*"[^"]*"' "$manifest" | grep -o '"[^"]*"$' | tr -d '"' | head -c 100)

        git -C "$REPO_PATH" commit -m "fix(harness): auto-repair $feature_id — $skill_name

Repair ID: $repair_id
Feature: $feature_id ($skill_name)
Model: $HARNESS_MODEL
Instance: $(hostname)

Ref: $(basename "$manifest")
" 2>/dev/null || true

        echo -e "    ${_GREEN}Commit criado no branch $branch_name${_NC}"

        # Auto PR
        if [ "$AUTO_PR" = "1" ] && command -v gh >/dev/null 2>&1; then
          git -C "$REPO_PATH" push origin "$branch_name" 2>/dev/null && \
          gh pr create --repo elderbernardi/exocortex.saas \
            --base main --head "$branch_name" \
            --title "fix(harness): auto-repair $feature_id" \
            --body "Reparo automático pelo harness de verificação.

Repair ID: \`$repair_id\`
Feature: \`$feature_id\` ($skill_name)
Files changed: $changed_files

---
*Criado automaticamente por sync-repairs-to-repo.sh*" \
            --label "auto-repair" 2>/dev/null && \
          echo -e "    ${_GREEN}PR criado${_NC}" || \
          echo -e "    ${_YELLOW}⚠ Falha ao criar PR${_NC}"
        fi

        # Update manifest
        sed -i 's/"sync_status": "pending"/"sync_status": "synced"/' "$manifest"
      else
        echo -e "    ${_GRAY}Sem diferenças para sincronizar${_NC}"
        sed -i 's/"sync_status": "pending"/"sync_status": "no_diff"/' "$manifest"
      fi
    else
      echo -e "    ${_YELLOW}⚠ Skill dir não encontrado em instância ou repo${_NC}"
    fi

    # Return to main
    git -C "$REPO_PATH" checkout main 2>/dev/null || true
  done

# =============================================================================
# Modo B: Sem repo local — gerar patches
# =============================================================================
else
  echo -e "  Modo: ${_YELLOW}B (sem repo local)${_NC} — gerando patches"
  echo -e "  ${_GRAY}Defina EXOCORTEX_REPO_PATH para sync direto${_NC}"
  echo ""

  mkdir -p "$PATCHES_DIR"

  for manifest in "${pending_manifests[@]}"; do
    repair_id=$(grep -o '"repair_id"[[:space:]]*:[[:space:]]*"[^"]*"' "$manifest" | grep -o '"[^"]*"$' | tr -d '"')
    feature_id=$(grep -o '"feature_id"[[:space:]]*:[[:space:]]*"[^"]*"' "$manifest" | grep -o '"[^"]*"$' | tr -d '"')
    skill_name=$(grep -o '"skill_name"[[:space:]]*:[[:space:]]*"[^"]*"' "$manifest" | grep -o '"[^"]*"$' | tr -d '"')

    echo -e "  ${_CYAN}Gerando patch: $repair_id ($feature_id)${_NC}"

    patch_file="$PATCHES_DIR/${repair_id}.patch"
    echo "# Patch: $repair_id" > "$patch_file"
    echo "# Feature: $feature_id ($skill_name)" >> "$patch_file"
    echo "# Gerado: $(date -Iseconds)" >> "$patch_file"
    echo "# Instance: $(hostname)" >> "$patch_file"
    echo "" >> "$patch_file"

    instance_skill_dir="$HERMES_HOME/skills/excrtx/$skill_name"
    if [ -d "$instance_skill_dir" ]; then
      echo "## Arquivos modificados na instância:" >> "$patch_file"
      find "$instance_skill_dir" -type f -newer "$manifest" -exec echo "  {}" \; >> "$patch_file"
      echo "" >> "$patch_file"
      echo "## Conteúdo dos arquivos:" >> "$patch_file"
      find "$instance_skill_dir" -type f -name "*.md" -newer "$manifest" -exec sh -c \
        'echo "### $1"; echo "```"; cat "$1"; echo "```"; echo ""' _ {} \; >> "$patch_file"
    fi

    echo -e "    ${_GREEN}Patch salvo: $patch_file${_NC}"

    # Create issue via Hermes headless
    if command -v hermes >/dev/null 2>&1; then
      hermes --model "$HARNESS_MODEL" --headless --prompt \
        "Crie issue no repositório elderbernardi/exocortex.saas:
        Título: [SYNC] Auto-repair $feature_id — patch disponível
        Labels: auto-repair, sync
        Corpo: Repair $repair_id gerou correções na instância $(hostname).
        Patch disponível em: $patch_file
        Aplicar com: cp dos arquivos da instância para o repo." 2>/dev/null || true
    fi

    sed -i 's/"sync_status": "pending"/"sync_status": "patch_saved"/' "$manifest"
  done
fi

echo ""
echo -e "${_GREEN}━━━ Sync completo ━━━${_NC}"
