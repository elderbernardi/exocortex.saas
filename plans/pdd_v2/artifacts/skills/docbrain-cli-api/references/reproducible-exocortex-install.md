# Reproducible Exocortex Install — DocBrain Parser Engine

## Context

DocBrain is the local document parser engine for Exocortex intake workflows. A new Exocortex install must not assume this current filesystem already exists; it must clone and configure DocBrain.

## Canonical repository

```bash
https://github.com/ProjetoBB/docBrainBB.git
```

## Default install path

```bash
${EXOCORTEX_DOCBRAIN_DIR:-$HOME/projetos/pessoal/projetob/docbrain}
```

## Install sequence

```bash
DOCBRAIN_DIR="${EXOCORTEX_DOCBRAIN_DIR:-$HOME/projetos/pessoal/projetob/docbrain}"
mkdir -p "$(dirname "$DOCBRAIN_DIR")"

if [ ! -d "$DOCBRAIN_DIR/.git" ]; then
  git clone https://github.com/ProjetoBB/docBrainBB.git "$DOCBRAIN_DIR"
fi

cd "$DOCBRAIN_DIR"
git pull --ff-only origin main
npm install
npm run build
npm run --silent cli -- api health --output json
```

## Key policy

Use the main Hermes key for DocBrain by default:

```bash
OPENROUTER_API_KEY
```

DocBrain-specific override, only when explicitly needed:

```bash
DOCBRAIN_LLM_API_KEY
```

Runtime precedence:

1. `DOCBRAIN_LLM_API_KEY`
2. `OPENROUTER_API_KEY`

## Missing key behavior

Do not block install if no key is available. Create a non-secret reminder:

```bash
mkdir -p "${HERMES_HOME:-$HOME/.hermes}/reminders"
cat > "${HERMES_HOME:-$HOME/.hermes}/reminders/docbrain-llm-key.md" <<'EOF'
# Pending DocBrain LLM key

DocBrain is installed, but no main Hermes LLM key was available during setup.

When the key exists, configure it as OPENROUTER_API_KEY in the Hermes environment. DocBrain will reuse it automatically.

Validation:
cd "$HOME/projetos/pessoal/projetob/docbrain"
npm run --silent cli -- api health --output json
EOF
```

## Setup-project replication

When documenting or changing DocBrain setup, update all three layers:

1. DocBrain repo docs:
   - `docs/HERMES-INTEGRATION.md`
   - `docs/CLI-API-CONTRACT.md`
   - `docs/EXOCORTEX-INSTALLATION.md`
2. Hermes local skill:
   - `~/.hermes/skills/exocortex/docbrain-cli-api/SKILL.md`
3. Setup microverso in the Acervo:
   - `~/.hermes/acervo/micro/hermes-setup/tools/docbrain-cli-api.md`
   - `~/.hermes/acervo/micro/hermes-setup/workflows/install-docbrain-parser-engine.md`
   - `~/.hermes/acervo/micro/hermes-setup/skills/docbrain-cli-api.md`
   - update `index.md`, `log.md`, and `workflows/replicable-exocortex-setup.md`

The Acervo setup microverso is not optional: it is the reproducibility record for future Exocortex installs.
