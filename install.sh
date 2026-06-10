1|#!/usr/bin/env bash
2|# =============================================================================
3|# Exocórtex.IA — Bootstrap Installer
4|# =============================================================================
5|# Instala Hermes Agent (se necessário) e o Exocórtex.IA com um comando:
6|#
7|#   curl -fsSL https://raw.githubusercontent.com/elderbernardi/exocortex.saas/main/install.sh | bash
8|#
9|# Com Telegram:
10|#   TELEGRAM_BOT_TOKEN="seu_token" curl -fsSL ... | bash
11|#
12|# Versão específica:
13|#   VERSION=v1.0.0-rc2 curl -fsSL ... | bash
14|#
15|# Ref: https://github.com/elderbernardi/exocortex.saas
16|# =============================================================================
17|
18|set -euo pipefail
19|
20|# ─── Colors ──────────────────────────────────────────────────────────────────
21|RED='\033[0;31m'
22|GREEN='\033[0;32m'
23|YELLOW='\033[1;33m'
24|CYAN='\033[0;36m'
25|BOLD='\033[1m'
26|NC='\033[0m'
27|
28|log()  { echo -e "${GREEN}✓${NC} $1"; }
29|warn() { echo -e "${YELLOW}⚠${NC} $1"; }
30|info() { echo -e "${CYAN}ℹ${NC} $1"; }
31|fail() { echo -e "${RED}✗${NC} $1"; exit 1; }
32|
33|# ─── Configuration ───────────────────────────────────────────────────────────
34|REPO_URL="https://github.com/elderbernardi/exocortex.saas.git"
35|REPO_API="https://api.github.com/repos/elderbernardi/exocortex.saas"
36|HERMES_INSTALLER="https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh"
37|INSTALLER_DIR="${EXOCORTEX_INSTALLER_DIR:-$HOME/.exocortex-installer}"
38|HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
39|EXOCORTEX_HOME="${EXOCORTEX_HOME:-$HOME/exocortex}"
40|
41|# ─── Banner ──────────────────────────────────────────────────────────────────
42|echo ''
43|echo -e "${BOLD}╔═══════════════════════════════════════════════════════════╗${NC}"
44|echo -e "${BOLD}║${NC}   ${CYAN}Exocórtex.IA${NC} — Instalador                              ${BOLD}║${NC}"
45|echo -e "${BOLD}║${NC}   Exoesqueleto para o pensamento                          ${BOLD}║${NC}"
46|echo -e "${BOLD}╚═══════════════════════════════════════════════════════════╝${NC}"
47|echo ''
48|
49|# ─── Step 1: Detect OS ──────────────────────────────────────────────────────
50|OS="$(uname -s)"
51|case "$OS" in
52|  Linux*)  OS_NAME="Linux" ;;
53|  Darwin*) OS_NAME="macOS" ;;
54|  *)       fail "Sistema operacional não suportado: $OS" ;;
55|esac
56|info "Sistema: $OS_NAME ($(uname -m))"
57|
58|# ─── Step 2: Check and install dependencies ─────────────────────────────────
59|info "Verificando dependências..."
60|
61|# Detect package manager
62|PKG_MGR=""
63|if command -v apt-get >/dev/null 2>&1; then
64|  PKG_MGR="apt"
65|elif command -v brew >/dev/null 2>&1; then
66|  PKG_MGR="brew"
67|elif command -v dnf >/dev/null 2>&1; then
68|  PKG_MGR="dnf"
69|elif command -v pacman >/dev/null 2>&1; then
70|  PKG_MGR="pacman"
71|fi
72|
73|# sudo helper: use sudo only if not root
74|SUDO=""
75|if [ "$(id -u)" -ne 0 ]; then
76|  if command -v sudo >/dev/null 2>&1; then
77|    SUDO="sudo"
78|  fi
79|fi
80|
81|install_packages() {
82|  local pkgs=("$@")
83|  if [ ${#pkgs[@]} -eq 0 ]; then return 0; fi
84|
85|  info "Instalando: ${pkgs[*]}..."
86|  case "$PKG_MGR" in
87|    apt)
88|      $SUDO apt-get update -qq >/dev/null 2>&1
89|      $SUDO apt-get install -y -qq "${pkgs[@]}" >/dev/null 2>&1
90|      ;;
91|    brew)
92|      brew install "${pkgs[@]}" >/dev/null 2>&1
93|      ;;
94|    dnf)
95|      $SUDO dnf install -y -q "${pkgs[@]}" >/dev/null 2>&1
96|      ;;
97|    pacman)
98|      $SUDO pacman -S --noconfirm "${pkgs[@]}" >/dev/null 2>&1
99|      ;;
100|    *)
101|      fail "Gerenciador de pacotes não detectado. Instale manualmente: ${pkgs[*]}"
102|      ;;
103|  esac
104|}
105|
106|# Check core deps
107|MISSING_DEPS=()
108|for cmd in git curl rsync; do
109|  if ! command -v "$cmd" >/dev/null 2>&1; then
110|    MISSING_DEPS+=("$cmd")
111|  fi
112|done
113|
114|# Check Python 3
115|PYTHON_PKGS=()
116|if ! command -v python3 >/dev/null 2>&1; then
117|  case "$PKG_MGR" in
118|    apt) PYTHON_PKGS=(python3 python3-pip python3-venv) ;;
119|    brew) PYTHON_PKGS=(python@3.11) ;;
120|    dnf) PYTHON_PKGS=(python3 python3-pip) ;;
121|    pacman) PYTHON_PKGS=(python python-pip) ;;
122|  esac
123|fi
124|
125|# Install if anything is missing
126|if [ ${#MISSING_DEPS[@]} -gt 0 ] || [ ${#PYTHON_PKGS[@]} -gt 0 ]; then
127|  ALL_PKGS=("${MISSING_DEPS[@]}" "${PYTHON_PKGS[@]}")
128|  install_packages "${ALL_PKGS[@]}"
129|
130|  # Verify after install
131|  for cmd in git curl rsync python3; do
132|    if ! command -v "$cmd" >/dev/null 2>&1; then
133|      fail "$cmd não encontrado após instalação. Instale manualmente."
134|    fi
135|  done
136|fi
137|
138|log "Dependências OK (git, curl, rsync, python3)"
139|
140|# ─── Step 3: Install Hermes (if not present) ────────────────────────────────
141|if command -v hermes >/dev/null 2>&1; then
142|  HERMES_VERSION=$(hermes --version 2>/dev/null | head -1)
143|  log "Hermes já instalado: $HERMES_VERSION"
144|else
145|  echo ''
146|  info "Hermes Agent não encontrado. Instalando..."
147|  info "Fonte: github.com/NousResearch/hermes-agent"
148|  echo ''
149|
150|  if curl -fsSL "$HERMES_INSTALLER" | bash; then
151|    # Reload PATH (Hermes installer adds to ~/.local/bin)
152|    export PATH="$HOME/.local/bin:$PATH"
153|
154|    if command -v hermes >/dev/null 2>&1; then
155|      HERMES_VERSION=$(hermes --version 2>/dev/null | head -1)
156|      log "Hermes instalado: $HERMES_VERSION"
157|    else
158|      fail "Hermes instalado mas 'hermes' não encontrado no PATH.
159|  Adicione ao PATH: export PATH=\"\$HOME/.local/bin:\$PATH\"
160|  E re-execute este instalador."
161|    fi
162|  else
163|    fail "Falha ao instalar Hermes. Verifique sua conexão e tente novamente."
164|  fi
165|fi
166|
167|# ─── Step 4: Resolve version ────────────────────────────────────────────────
168|if [ -n "${VERSION:-}" ]; then
169|  INSTALL_VERSION="$VERSION"
170|  info "Versão solicitada: $INSTALL_VERSION"
171|else
172|  info "Consultando versão mais recente..."
173|
174|  # Try GitHub API for latest tag
175|  if command -v jq >/dev/null 2>&1; then
176|    INSTALL_VERSION=$(curl -fsSL "${REPO_API}/tags" 2>/dev/null | jq -r '.[0].name // empty' 2>/dev/null || true)
177|  else
178|    # Fallback without jq: parse JSON with grep/sed
179|    INSTALL_VERSION=$(curl -fsSL "${REPO_API}/tags" 2>/dev/null | grep -m1 '"name"' | sed 's/.*"name": *"\([^"]*\)".*/\1/' || true)
180|  fi
181|
182|  if [ -z "$INSTALL_VERSION" ]; then
183|    warn "Não foi possível determinar a tag mais recente. Usando 'release-candidate'."
184|    INSTALL_VERSION="release-candidate"
185|  fi
186|
187|  info "Versão: $INSTALL_VERSION"
188|fi
189|
190|# ─── Step 5: Download/update installer ───────────────────────────────────────
191|echo ''
192|info "Diretório do instalador: $INSTALLER_DIR"
193|
194|VERSION_FILE="$INSTALLER_DIR/.exocortex-version"
195|NEEDS_DOWNLOAD=true
196|
197|if [ -d "$INSTALLER_DIR/.git" ]; then
198|  CURRENT_VERSION=$(cat "$VERSION_FILE" 2>/dev/null || echo "unknown")
199|  if [ "$CURRENT_VERSION" = "$INSTALL_VERSION" ]; then
200|    info "Versão $INSTALL_VERSION já baixada. Re-executando setup..."
201|    NEEDS_DOWNLOAD=false
202|  else
203|    info "Atualizando de $CURRENT_VERSION para $INSTALL_VERSION..."
204|    rm -rf "$INSTALLER_DIR"
205|  fi
206|fi
207|
208|if $NEEDS_DOWNLOAD; then
209|  info "Baixando Exocórtex.IA ($INSTALL_VERSION)..."
210|
211|  if git clone --depth 1 --branch "$INSTALL_VERSION" "$REPO_URL" "$INSTALLER_DIR" 2>/dev/null; then
212|    echo "$INSTALL_VERSION" > "$VERSION_FILE"
213|    log "Download completo"
214|  else
215|    # Fallback: try without --branch (might be a commit hash or branch name issue)
216|    if git clone --depth 1 "$REPO_URL" "$INSTALLER_DIR" 2>/dev/null; then
217|      cd "$INSTALLER_DIR"
218|      git fetch --depth 1 origin "refs/tags/$INSTALL_VERSION:refs/tags/$INSTALL_VERSION" 2>/dev/null || true
219|      git checkout "$INSTALL_VERSION" 2>/dev/null || warn "Tag $INSTALL_VERSION não encontrada; usando main"
220|      echo "$INSTALL_VERSION" > "$VERSION_FILE"
221|      log "Download completo (fallback)"
222|    else
223|      fail "Falha ao clonar repositório. Verifique sua conexão:
224|  URL: $REPO_URL
225|  Tag: $INSTALL_VERSION"
226|    fi
227|  fi
228|fi
229|
230|# ─── Step 6: Run setup.sh ───────────────────────────────────────────────────
231|echo ''
232|info "Executando setup..."
233|echo ''
234|
235|cd "$INSTALLER_DIR"
236|
237|# Locate setup.sh — could be at root (release-candidate) or in plans/pdd_v2/artifacts/
238|if [ -f "setup.sh" ]; then
239|  SETUP_PATH="."
240|elif [ -f "plans/pdd_v2/artifacts/setup.sh" ]; then
241|  SETUP_PATH="plans/pdd_v2/artifacts"
242|else
243|  fail "setup.sh não encontrado no instalador. Versão corrompida?"
244|fi
245|
246|cd "$SETUP_PATH"
247|
248|HERMES_HOME="$HERMES_HOME" \
249|EXOCORTEX_HOME="$EXOCORTEX_HOME" \
250|TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}" \
251|bash setup.sh
252|
253|# ─── Step 7: Success banner ─────────────────────────────────────────────────
254|echo ''
255|echo -e "${BOLD}╔═══════════════════════════════════════════════════════════╗${NC}"
256|echo -e "${BOLD}║${NC}   ${GREEN}✅ Exocórtex.IA instalado com sucesso!${NC}                  ${BOLD}║${NC}"
257|echo -e "${BOLD}╚═══════════════════════════════════════════════════════════╝${NC}"
258|echo ''
259|echo -e "  Versão:    ${CYAN}$INSTALL_VERSION${NC}"
260|echo -e "  Hermes:    ${CYAN}$(hermes --version 2>/dev/null | head -1 || echo 'ver PATH')${NC}"
261|echo -e "  Skills:    ${CYAN}$(find "$HERMES_HOME/skills/excrtx" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')${NC}"
262|echo -e "  Runtime:   ${CYAN}$HERMES_HOME${NC}"
263|echo -e "  Workspace: ${CYAN}$EXOCORTEX_HOME${NC}"
264|echo -e "  Installer: ${CYAN}$INSTALLER_DIR${NC}"
265|echo ''
266|echo -e "  ${BOLD}Próximos passos:${NC}"
267|echo -e "    ${GREEN}hermes${NC}                          # iniciar sessão interativa"
268|echo -e "    ${GREEN}hermes -p manut${NC}                 # modo manutenção"
268b|echo -e "    ${GREEN}hermes -p chat${NC}                  # modo chat (sem harness)"
269|echo ''
270|
271|# Telegram status
272|if [ -n "${TELEGRAM_BOT_TOKEN:-}" ]; then
273|  echo -e "    ${GREEN}✓${NC} Telegram configurado"
274|else
275|  echo -e "    ${YELLOW}Telegram:${NC} Para configurar, re-execute com:"
276|  echo -e "    ${CYAN}TELEGRAM_BOT_TOKEN=\"seu_token\" bash $INSTALLER_DIR/install.sh${NC}"
277|fi
278|
279|# Google status
280|if [ -f "$HERMES_HOME/reminders/google-credentials.md" ]; then
281|  echo -e "    ${YELLOW}Google:${NC}   gcloud auth application-default login"
282|fi
283|
284|echo ''
285|echo -e "  ${BOLD}Re-run / atualizar:${NC}"
286|echo -e "    ${CYAN}bash $INSTALLER_DIR/install.sh${NC}"
287|echo -e "    ${CYAN}VERSION=<tag> bash $INSTALLER_DIR/install.sh${NC}"
288|echo ''
289|