---
title: Workflow — Instalar DocBrain em Novos Exocórtex
created: 2026-05-31
updated: 2026-05-31
nature: processos
kind: workflow
scope_mode: micro
scope_slug: hermes-setup
applies_to: [global]
authority: canonical
operational_mode: executable
stability: active
sources:
  - /home/elder/projetos/pessoal/projetob/docbrain/docs/EXOCORTEX-INSTALLATION.md
  - ~/.hermes/setup.sh
derived_from:
  - docbrain-cli-api
confidence: high
promotion_policy: candidate-global
upstream:
  source_skill: exocortex/docbrain-cli-api
  assumed_version: 1.0.0
  coupling: adapter-only
tags: [setup, docbrain, parser, intake, reproducibility]
---

# Workflow — Instalar DocBrain em Novos Exocórtex

Todo novo Exocórtex que precise de intake documental deve instalar o DocBrain como engine local de parser.

## Instalação

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
```

## Política de key

A key do DocBrain deve ser a mesma key main do Hermes.

Preferência:

```bash
OPENROUTER_API_KEY
```

Override específico, só quando necessário:

```bash
DOCBRAIN_LLM_API_KEY
```

Precedência no runtime:

1. `DOCBRAIN_LLM_API_KEY`
2. `OPENROUTER_API_KEY`

## Sem key no momento da instalação

Não bloquear o setup. Criar lembrança sem segredo:

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

## Validação

```bash
cd "$DOCBRAIN_DIR"
npm run --silent cli -- api health --output json
npx vitest run --pool=forks
npm run lint
npm run build
```

## Critério de pronto

- Repo clonado.
- `npm install` executado.
- `npm run build` executado.
- `api health` retorna `ok=true`.
- `OPENROUTER_API_KEY` existe ou o lembrete foi criado.
- Hermes tem acesso de terminal ao workspace DocBrain.
