1|#!/usr/bin/env bash
2|# =============================================================================
3|# Exocórtex — Sync Repairs to Repository
4|# =============================================================================
5|# Protocolo de sincronização: instância Hermes → repositório exocortex.saas
6|# Lê repair manifests e aplica mudanças de volta ao repo fonte.
7|#
8|# Modo A: EXOCORTEX_REPO_PATH definido → branch + commit + (opcional) PR
9|# Modo B: Sem repo local → gerar patch + issue via Hermes headless
10|#
11|# Uso:
12|#   bash scripts/sync-repairs-to-repo.sh
13|#
14|# Variáveis de ambiente:
15|#   EXOCORTEX_REPO_PATH    Path do clone local do repo
16|#   EXOCORTEX_SYNC_AUTO_PR Se 1, cria PR via gh CLI
17|#   ACERVO                 Path do acervo na instância
18|#   HERMES_HOME            Path do Hermes home na instância
19|# =============================================================================
20|
21|set -uo pipefail
22|
23|SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
24|
25|# Config
26|ACERVO="${ACERVO:-${EXOCORTEX_HOME:-$HOME/exocortex}/acervo}"
27|HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
28|REPO_PATH="${EXOCORTEX_REPO_PATH:-}"
29|AUTO_PR="${EXOCORTEX_SYNC_AUTO_PR:-0}"
30|HARNESS_MODEL="${EXOCORTEX_HARNESS_MODEL:-openai/gpt-5.4}"
31|REPAIRS_DIR="$ACERVO/_artifacts/items/repairs"
32|PATCHES_DIR="$ACERVO/_artifacts/items/patches"
33|
34|_RED='\033[0;31m'
35|_GREEN='\033[0;32m'
36|_YELLOW='\033[1;33m'
37|_CYAN='\033[0;36m'
38|_GRAY='\033[0;90m'
39|_NC='\033[0m'
40|
41|# =============================================================================
42|# Allowlist / Blocklist
43|# =============================================================================
44|
45|# Paths que podem ser sincronizados (instância → repo)
46|ALLOWED_SYNC_PREFIXES=(
47|  "skills/excrtx/excrtx-"     # Skills
48|  "acervo/global/templates/"     # Templates seed
49|  "acervo/global/tools/"         # Harness tools
50|  "acervo/global/contracts/"     # Contracts
51|  "acervo/global/workflows/"     # Workflows
52|  "acervo/micro/_template/"      # Microverso template
53|  "profiles/"                    # Profiles
54|  "skill-bundles/"               # Bundles
55|)
56|
57|# Paths que NUNCA devem ser sincronizados
58|BLOCKED_PATTERNS=(
59|  "macro/soul.md"
60|  "macro/valores.md"
61|  "macro/estilo.md"
62|  "SOUL.md"
63|  "memories/"
64|  "credential"
65|  "token"
66|  "secret"
67|  ".env"
68|  "__pycache__"
69|)
70|
71|is_path_allowed() {
72|  local path="$1"
73|
74|  # Check blocklist first
75|  for pattern in "${BLOCKED_PATTERNS[@]}"; do
76|    if [[ "$path" == *"$pattern"* ]]; then
77|      return 1
78|    fi
79|  done
80|
81|  # Check allowlist
82|  for prefix in "${ALLOWED_SYNC_PREFIXES[@]}"; do
83|    if [[ "$path" == *"$prefix"* ]]; then
84|      return 0
85|    fi
86|  done
87|
88|  return 1  # not in allowlist
89|}
90|
91|# Map instance path to repo path
92|instance_to_repo_path() {
93|  local ipath="$1"
94|
95|  # Skills: $HERMES_HOME/skills/excrtx/<skill>/ → skills/<skill>/
96|  if [[ "$ipath" == *"/skills/excrtx/"* ]]; then
97|    echo "skills/${ipath##*/skills/excrtx/}"
98|    return
99|  fi
100|
101|  # Acervo: $ACERVO/<rest> → acervo/<rest>
102|  if [[ "$ipath" == "$ACERVO/"* ]]; then
103|    echo "acervo/${ipath#$ACERVO/}"
104|    return
105|  fi
106|
107|  # Profiles: $HERMES_HOME/profiles/ → profiles/
108|  if [[ "$ipath" == *"/profiles/"* ]]; then
109|    echo "profiles/${ipath##*/profiles/}"
110|    return
111|  fi
112|
113|  echo ""  # not mappable
114|}
115|
116|# =============================================================================
117|# Main
118|# =============================================================================
119|
120|echo ""
121|echo -e "${_CYAN}━━━ Sync de Reparos: Instância → Repositório ━━━${_NC}"
122|echo ""
123|
124|# Find pending repair manifests
125|if [ ! -d "$REPAIRS_DIR" ]; then
126|  echo -e "  ${_GRAY}Sem diretório de repairs: $REPAIRS_DIR${_NC}"
127|  exit 0
128|fi
129|
130|pending_manifests=()
131|for manifest in "$REPAIRS_DIR"/RPR-*.json; do
132|  [ -f "$manifest" ] || continue
133|  status=$(grep -o '"sync_status"[[:space:]]*:[[:space:]]*"[^"]*"' "$manifest" | grep -o '"[^"]*"$' | tr -d '"')
134|  if [ "$status" = "pending" ]; then
135|    pending_manifests+=("$manifest")
136|  fi
137|done
138|
139|if [ ${#pending_manifests[@]} -eq 0 ]; then
140|  echo -e "  ${_GREEN}Nenhum reparo pendente de sync.${_NC}"
141|  exit 0
142|fi
143|
144|echo -e "  Reparos pendentes: ${#pending_manifests[@]}"
145|
146|# =============================================================================
147|# Modo A: Repo local disponível
148|# =============================================================================
149|if [ -n "$REPO_PATH" ] && [ -d "$REPO_PATH/.git" ]; then
150|  echo -e "  Modo: ${_GREEN}A (repo local)${_NC} — $REPO_PATH"
151|  echo ""
152|
153|  # Ensure clean state
154|  if ! git -C "$REPO_PATH" diff --quiet 2>/dev/null; then
155|    echo -e "  ${_YELLOW}⚠ Repo tem mudanças não commitadas. Sync abortado.${_NC}"
156|    exit 1
157|  fi
158|
159|  for manifest in "${pending_manifests[@]}"; do
160|    repair_id=$(grep -o '"repair_id"[[:space:]]*:[[:space:]]*"[^"]*"' "$manifest" | grep -o '"[^"]*"$' | tr -d '"')
161|    feature_id=$(grep -o '"feature_id"[[:space:]]*:[[:space:]]*"[^"]*"' "$manifest" | grep -o '"[^"]*"$' | tr -d '"')
162|    skill_name=$(grep -o '"skill_name"[[:space:]]*:[[:space:]]*"[^"]*"' "$manifest" | grep -o '"[^"]*"$' | tr -d '"')
163|
164|    echo -e "  ${_CYAN}Processing: $repair_id ($feature_id)${_NC}"
165|
166|    # Create branch
167|    branch_name="repair/${repair_id}"
168|    git -C "$REPO_PATH" checkout -b "$branch_name" main 2>/dev/null || \
169|    git -C "$REPO_PATH" checkout -b "$branch_name" 2>/dev/null || true
170|
171|    # Diff and copy skill files
172|    instance_skill_dir="$HERMES_HOME/skills/excrtx/$skill_name"
173|    repo_skill_dir="$REPO_PATH/skills/$skill_name"
174|
175|    if [ -d "$instance_skill_dir" ] && [ -d "$repo_skill_dir" ]; then
176|      changed_files=0
177|      while IFS= read -r file; do
178|        rel_path="${file#$instance_skill_dir/}"
179|        repo_file="$repo_skill_dir/$rel_path"
180|
181|        # Check allowlist
182|        if ! is_path_allowed "skills/excrtx/$skill_name/$rel_path"; then
183|          echo -e "    ${_GRAY}Skip (blocklist): $rel_path${_NC}"
184|          continue
185|        fi
186|
187|        # Diff
188|        if [ -f "$repo_file" ]; then
189|          if ! diff -q "$file" "$repo_file" >/dev/null 2>&1; then
190|            local diff_lines
191|            diff_lines=$(diff -u "$repo_file" "$file" | wc -l)
192|            if [ "$diff_lines" -gt 200 ]; then
193|              echo -e "    ${_YELLOW}⚠ Diff muito grande ($diff_lines linhas): $rel_path — escalar para review${_NC}"
194|              continue
195|            fi
196|            cp "$file" "$repo_file"
197|            git -C "$REPO_PATH" add "skills/$skill_name/$rel_path"
198|            changed_files=$((changed_files + 1))
199|            echo -e "    ${_GREEN}✓${_NC} Atualizado: $rel_path"
200|          fi
201|        else
202|          # New file
203|          mkdir -p "$(dirname "$repo_file")"
204|          cp "$file" "$repo_file"
205|          git -C "$REPO_PATH" add "skills/$skill_name/$rel_path"
206|          changed_files=$((changed_files + 1))
207|          echo -e "    ${_GREEN}+${_NC} Novo: $rel_path"
208|        fi
209|      done < <(find "$instance_skill_dir" -type f)
210|
211|      if [ $changed_files -gt 0 ]; then
212|        # Commit
213|        local error_desc
214|        error_desc=$(grep -o '"error"[[:space:]]*:[[:space:]]*"[^"]*"' "$manifest" | grep -o '"[^"]*"$' | tr -d '"' | head -c 100)
215|
216|        git -C "$REPO_PATH" commit -m "fix(harness): auto-repair $feature_id — $skill_name
217|
218|Repair ID: $repair_id
219|Feature: $feature_id ($skill_name)
220|Model: $HARNESS_MODEL
221|Instance: $(hostname)
222|
223|Ref: $(basename "$manifest")
224|" 2>/dev/null || true
225|
226|        echo -e "    ${_GREEN}Commit criado no branch $branch_name${_NC}"
227|
228|        # Auto PR
229|        if [ "$AUTO_PR" = "1" ] && command -v gh >/dev/null 2>&1; then
230|          git -C "$REPO_PATH" push origin "$branch_name" 2>/dev/null && \
231|          gh pr create --repo elderbernardi/exocortex.saas \
232|            --base main --head "$branch_name" \
233|            --title "fix(harness): auto-repair $feature_id" \
234|            --body "Reparo automático pelo harness de verificação.
235|
236|Repair ID: \`$repair_id\`
237|Feature: \`$feature_id\` ($skill_name)
238|Files changed: $changed_files
239|
240|---
241|*Criado automaticamente por sync-repairs-to-repo.sh*" \
242|            --label "auto-repair" 2>/dev/null && \
243|          echo -e "    ${_GREEN}PR criado${_NC}" || \
244|          echo -e "    ${_YELLOW}⚠ Falha ao criar PR${_NC}"
245|        fi
246|
247|        # Update manifest
248|        sed -i 's/"sync_status": "pending"/"sync_status": "synced"/' "$manifest"
249|      else
250|        echo -e "    ${_GRAY}Sem diferenças para sincronizar${_NC}"
251|        sed -i 's/"sync_status": "pending"/"sync_status": "no_diff"/' "$manifest"
252|      fi
253|    else
254|      echo -e "    ${_YELLOW}⚠ Skill dir não encontrado em instância ou repo${_NC}"
255|    fi
256|
257|    # Return to main
258|    git -C "$REPO_PATH" checkout main 2>/dev/null || true
259|  done
260|
261|# =============================================================================
262|# Modo B: Sem repo local — gerar patches
263|# =============================================================================
264|else
265|  echo -e "  Modo: ${_YELLOW}B (sem repo local)${_NC} — gerando patches"
266|  echo -e "  ${_GRAY}Defina EXOCORTEX_REPO_PATH para sync direto${_NC}"
267|  echo ""
268|
269|  mkdir -p "$PATCHES_DIR"
270|
271|  for manifest in "${pending_manifests[@]}"; do
272|    repair_id=$(grep -o '"repair_id"[[:space:]]*:[[:space:]]*"[^"]*"' "$manifest" | grep -o '"[^"]*"$' | tr -d '"')
273|    feature_id=$(grep -o '"feature_id"[[:space:]]*:[[:space:]]*"[^"]*"' "$manifest" | grep -o '"[^"]*"$' | tr -d '"')
274|    skill_name=$(grep -o '"skill_name"[[:space:]]*:[[:space:]]*"[^"]*"' "$manifest" | grep -o '"[^"]*"$' | tr -d '"')
275|
276|    echo -e "  ${_CYAN}Gerando patch: $repair_id ($feature_id)${_NC}"
277|
278|    patch_file="$PATCHES_DIR/${repair_id}.patch"
279|    echo "# Patch: $repair_id" > "$patch_file"
280|    echo "# Feature: $feature_id ($skill_name)" >> "$patch_file"
281|    echo "# Gerado: $(date -Iseconds)" >> "$patch_file"
282|    echo "# Instance: $(hostname)" >> "$patch_file"
283|    echo "" >> "$patch_file"
284|
285|    instance_skill_dir="$HERMES_HOME/skills/excrtx/$skill_name"
286|    if [ -d "$instance_skill_dir" ]; then
287|      echo "## Arquivos modificados na instância:" >> "$patch_file"
288|      find "$instance_skill_dir" -type f -newer "$manifest" -exec echo "  {}" \; >> "$patch_file"
289|      echo "" >> "$patch_file"
290|      echo "## Conteúdo dos arquivos:" >> "$patch_file"
291|      find "$instance_skill_dir" -type f -name "*.md" -newer "$manifest" -exec sh -c \
292|        'echo "### $1"; echo "```"; cat "$1"; echo "```"; echo ""' _ {} \; >> "$patch_file"
293|    fi
294|
295|    echo -e "    ${_GREEN}Patch salvo: $patch_file${_NC}"
296|
297|    # Create issue via Hermes headless
298|    if command -v hermes >/dev/null 2>&1; then
299|      hermes --model "$HARNESS_MODEL" --headless --prompt \
300|        "Crie issue no repositório elderbernardi/exocortex.saas:
301|        Título: [SYNC] Auto-repair $feature_id — patch disponível
302|        Labels: auto-repair, sync
303|        Corpo: Repair $repair_id gerou correções na instância $(hostname).
304|        Patch disponível em: $patch_file
305|        Aplicar com: cp dos arquivos da instância para o repo." 2>/dev/null || true
306|    fi
307|
308|    sed -i 's/"sync_status": "pending"/"sync_status": "patch_saved"/' "$manifest"
309|  done
310|fi
311|
312|echo ""
313|echo -e "${_GREEN}━━━ Sync completo ━━━${_NC}"
314|