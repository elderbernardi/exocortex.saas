# Reproducible Exocortex Install — DocBrain Parser Engine

## Context

DocBrain is the local document parser engine for Exocortex intake workflows. A new Exocortex install must not assume this current filesystem already exists; it must clone and configure DocBrain.

## Canonical repository

```bash
https://github.com/ProjetoBB/docBrainBB.git
```

## Default install path

```bash
${EXOCORTEX_DOCBRAIN_DIR:-${EXOCORTEX_HOME:-$HOME/exocortex}/tools/docbrain}
```

## Install sequence

```bash
DOCBRAIN_DIR="${EXOCORTEX_DOCBRAIN_DIR:-${EXOCORTEX_HOME:-$HOME/exocortex}/tools/docbrain}"
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

DocBrain's LLM is driven by the Exocórtex **auxiliar** role (`EXOCORTEX_AUX_{PROVIDER,MODEL,API_KEY,BASE_URL}`). The aux role is reserved for external software (DocBrain, the Hindsight LLM backend) and inherits the **default** role field-by-field when left empty, so DocBrain reuses the main Hermes LLM by default.

The operator configures the aux role, never `DOCBRAIN_LLM_API_KEY` directly. `setup/step-08-integration-docbrain.sh` resolves the aux role (via `setup/lib/llm-roles.sh`) and writes DocBrain's `.env` (`DOCBRAIN_LLM_API_KEY/MODEL/BASE_URL`) from it. `DOCBRAIN_LLM_API_KEY` survives only as DocBrain's internal contract — generated, not hand-set.

## Missing key behavior

Do not block install if the aux role resolves to no key. Create a non-secret reminder:

```bash
mkdir -p "${HERMES_HOME:-$HOME/.hermes}/reminders"
cat > "${HERMES_HOME:-$HOME/.hermes}/reminders/docbrain-llm-key.md" <<'EOF'
# Pending DocBrain LLM key

DocBrain is installed, but the auxiliar LLM role resolved to no key during setup.

When a key is available, configure the auxiliar role (EXOCORTEX_AUX_*, which inherits the default role when empty) and re-run setup/step-08-integration-docbrain.sh. It regenerates DocBrain's .env (DOCBRAIN_LLM_API_KEY) from the role.

Validation:
DOCBRAIN_DIR="${EXOCORTEX_DOCBRAIN_DIR:-${EXOCORTEX_HOME:-$HOME/exocortex}/tools/docbrain}"
cd "$DOCBRAIN_DIR"
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
   - `~/.hermes/skills/exocortex/excrtx-integrate-docbrain/SKILL.md`
3. Setup microverso in the Acervo:
   - `~/.hermes/acervo/micro/hermes-setup/tools/excrtx-integrate-docbrain.md`
   - `~/.hermes/acervo/micro/hermes-setup/workflows/install-docbrain-parser-engine.md`
   - `~/.hermes/acervo/micro/hermes-setup/skills/excrtx-integrate-docbrain.md`
   - update `index.md`, `log.md`, and `workflows/replicable-exocortex-setup.md`

The Acervo setup microverso is not optional: it is the reproducibility record for future Exocortex installs.
