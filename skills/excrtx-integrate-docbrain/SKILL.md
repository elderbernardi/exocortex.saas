---
name: excrtx-integrate-docbrain
description: Use when Hermes or Exocórtex needs to parse documents through DocBrain,
  validate the local parser engine, or reproduce the DocBrain integration in a new
  Exocortex install.
version: 1.0.0
category: excrtx
platforms:
- linux
author: Exocórtex
license: MIT
metadata:
  hermes:
    tags:
    - exocortex
    - docbrain
    - parser
    - cli-api
    - intake
    - documents
    related_skills:
    - hermes-agent
    - excrtx-memory-manager
    calibration:
    - feature_id: EX-27
      calibration_prompt: Você deve garantir que as operações e regras da skill DocBrain
        Parser (excrtx-integrate-docbrain) estão totalmente ativas no seu comportamento
        e integridade.
      test_prompt: Verifique se o DocBrain repo está clonado e buildado.
      acceptance_criteria: O agente deve demonstrar de forma clara e factual que compreende
        as regras e procedimentos da skill DocBrain Parser.
      remediation_tip: Certifique-se de que a documentação e os limites da skill DocBrain
        Parser em seu SKILL.md estão sendo estritamente seguidos.
---
# DocBrain CLI API

## Overview

DocBrain is the local document parser engine for Exocortex intake workflows. Hermes consumes it through a machine-readable CLI API, not through an HTTP service.

The repository is:

```bash
https://github.com/ProjetoBB/docBrainBB.git
```

## When to Use

Use this skill when:

- parsing a PDF, Markdown, text file or local document for intake;
- checking whether DocBrain is available to Hermes;
- querying a previous parse job by `document_id` or `job_id`;
- reproducing DocBrain setup for a new Exocortex installation;
- debugging DocBrain CLI API output or idempotency.

Do not use the human `docbrain ingest` command for Hermes automation unless the goal is to update DocBrain's wiki projection.

## Key Policy

DocBrain must reuse the main Hermes LLM key when possible.

## Workspace Resolution

Do not assume the documented path is the live runtime path.
Before the first DocBrain action in a task, resolve the workspace by testing candidate directories and preferring the first one that passes the CLI API health check.

Recommended resolution order:

1. `$EXOCORTEX_DOCBRAIN_DIR` when explicitly set;
2. the current local tool copy used by Exocortex/Hermes workflows;
3. the documented canonical repository clone;
4. any other known DocBrain checkout the operator asked you to use.

Validation rule:

- a workspace is valid only if `npm run --silent cli -- api health --output json` returns `ok=true` and `api_version=docbrain.cli.v1`;
- if a checkout exists but the `api` command is missing or returns a different contract, treat that checkout as stale for Hermes automation and keep searching;
- only after resolving the workspace should you run parse or query commands.

Reminder hygiene:

- if a reminder file says the LLM key is missing, verify the live environment before trusting the reminder;
- stale reminders should not override a live environment that already exposes `DOCBRAIN_LLM_API_KEY` or `OPENROUTER_API_KEY`.

Preferred environment variable:

```bash
OPENROUTER_API_KEY
```

DocBrain-specific override:

```bash
DOCBRAIN_LLM_API_KEY
```

Runtime precedence:

1. `DOCBRAIN_LLM_API_KEY`
2. `OPENROUTER_API_KEY`

If no key exists during a new Exocortex install, do not block setup. Create a non-secret reminder at:

```bash
${HERMES_HOME:-$HOME/.hermes}/reminders/docbrain-llm-key.md
```

## Health Check

Run before the first DocBrain action in a task, after resolving the workspace:

```bash
DOCBRAIN_DIR="${EXOCORTEX_DOCBRAIN_DIR:-${EXOCORTEX_HOME:-$HOME/exocortex}/tools/docbrain}"
cd "$DOCBRAIN_DIR"
npm run --silent cli -- api health --output json
```

Expected:

- `ok=true`
- `api_version=docbrain.cli.v1`
- `command=health`

## Parse Document

Default Hermes call:

```bash
DOCBRAIN_DIR="${EXOCORTEX_DOCBRAIN_DIR:-${EXOCORTEX_HOME:-$HOME/exocortex}/tools/docbrain}"
cd "$DOCBRAIN_DIR"
npm run --silent cli -- api parse create \
  --input /abs/path/document.pdf \
  --include document,job,sections,tables \
  --reprocess-policy skip \
  --output json
```

Defaults for agents:

- use `--reprocess-policy skip`;
- request `document,job` by default;
- add `sections,tables` when the intake needs structured content;
- add `raw_text` only when the user or downstream workflow needs full text;
- do not write wiki files.

## Request via Stdin

Use stdin for complex requests:

```bash
DOCBRAIN_DIR="${EXOCORTEX_DOCBRAIN_DIR:-${EXOCORTEX_HOME:-$HOME/exocortex}/tools/docbrain}"
cd "$DOCBRAIN_DIR"
printf '%s' "$REQUEST_JSON" | npm run --silent cli -- api parse create --request -
```

Payload shape:

```json
{
  "input": "/abs/path/document.pdf",
  "input_kind": "file",
  "include": ["document", "job", "sections", "tables"],
  "reprocess_policy": "skip",
  "llm": "auto",
  "citation": "Documento recebido pelo intake",
  "tags": ["intake"],
  "project_root": "${EXOCORTEX_DOCBRAIN_DIR:-${EXOCORTEX_HOME:-$HOME/exocortex}/tools/docbrain}"
}
```

## Query Jobs

Latest by document id:

```bash
npm run --silent cli -- api parse get \
  --document-id 'sha256:...' \
  --latest \
  --include document,job
```

By job id:

```bash
npm run --silent cli -- api parse get \
  --job-id 'sha256_...-r1' \
  --include document,job
```

Recent jobs:

```bash
npm run --silent cli -- api parse list --limit 20 --status completed
```

Revisions:

```bash
npm run --silent cli -- api parse revisions --document-id 'sha256:...'
```

## New Exocortex Installation

Clone and configure DocBrain during setup:

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
```

If `OPENROUTER_API_KEY` exists in the Hermes environment, DocBrain will reuse it. If no key exists, create the reminder file and continue.

## Validation

Use this test command in the current environment:

```bash
DOCBRAIN_DIR="${EXOCORTEX_DOCBRAIN_DIR:-${EXOCORTEX_HOME:-$HOME/exocortex}/tools/docbrain}"
cd "$DOCBRAIN_DIR"
npx vitest run --pool=forks
npm run lint
npm run build
```

The default `npm test` can stall under Node v25 due to Vitest's default pool. Use the forked pool for reliable validation.

Manual JSON check:

```bash
DOCBRAIN_DIR="${EXOCORTEX_DOCBRAIN_DIR:-${EXOCORTEX_HOME:-$HOME/exocortex}/tools/docbrain}"
cd "$DOCBRAIN_DIR"
npm run --silent cli -- api health --output json > /tmp/docbrain-health.json
node -e "const fs=require('fs'); const j=JSON.parse(fs.readFileSync('/tmp/docbrain-health.json','utf8')); if(j.ok!==true || j.api_version!=='docbrain.cli.v1') process.exit(1);"
```

## Files to Read

Canonical docs in the DocBrain repository:

- `docs/HERMES-INTEGRATION.md`
- `docs/CLI-API-CONTRACT.md`
- `docs/EXOCORTEX-INSTALLATION.md`
- `plans/DOCBRAIN-INTAKE-ENGINE-REPORT.md`

Skill reference:

- `references/reproducible-exocortex-install.md` — clone/build/key policy and the required replication targets in the Hermes setup microverso.

## Reproducibility Rule

When updating DocBrain integration for Exocortex, do not stop at repo docs or the runtime skill. Also replicate the operational knowledge into the setup microverso:

- `~/.hermes/acervo/micro/hermes-setup/tools/excrtx-integrate-docbrain.md`
- `~/.hermes/acervo/micro/hermes-setup/workflows/install-docbrain-parser-engine.md`
- `~/.hermes/acervo/micro/hermes-setup/skills/excrtx-integrate-docbrain.md`
- update `index.md`, `log.md`, and `workflows/replicable-exocortex-setup.md`

The setup microverso is the reproducibility source for future Exocortex installs.

## Pitfalls

1. `docbrain` may not be installed globally. Use `npm run --silent cli -- ...` from the repository.
2. Do not expose API keys in docs, reminders or parse payloads.
3. Do not request `raw_text` by default; it can make responses large.
4. Do not use `ingest` for machine automation; use `api parse create`.
5. Keep `reprocess-policy=skip` as default to avoid repeated LLM/parser cost.

## Verification Checklist

- [ ] `api health` returns JSON with `ok=true`.
- [ ] `api parse create` returns `docbrain.cli.v1` envelope.
- [ ] Parse job contains `document_id`, `job_id` and `revision`.
- [ ] `raw_text` is omitted unless requested.
- [ ] `npx vitest run --pool=forks` passes before committing DocBrain changes.

## Procedure

Follow the steps and rules defined in this skill's body sections above.
