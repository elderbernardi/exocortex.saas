---
adr: "015"
titulo: "Skill Naming Convention"
status: aceito
data: 2026-06-04
decisores: ["executivo", "exocortex-team"]
---

# ADR-015: Skill Naming Convention

## Contexto

As 33 skills do Exocórtex RC1 usam nomes inconsistentes (`acervo-manager`, `stop-slop`, `taste-skill`, `codex-harness`, `exocortex-vetor-ativo`). Problemas:

1. **Descoberta pobre** — sem prefix comum, autocomplete não filtra skills do Exocórtex vs Hermes built-in vs plugins terceiros
2. **Classificação implícita ausente** — o nome não indica a natureza da skill (memória? qualidade? integração?)
3. **Extensibilidade frágil** — sem convenção, skills de terceiros colidem com nomes internos
4. **Referência cruzada** — SOUL_SEED.md, bundle YAML, profile YAML e setup.sh referenciam nomes; inconsistência gera drift

Referência: blog Anthropic "Lessons from Building Claude Code" (2026-06-03) — lições sobre nomenclatura, descrição trigger-first, e verificação por scripts.

## Decisão

### Padrão: `excrtx-{TYPE}-{NAME}`

Todas as skills core do Exocórtex seguem este padrão.

**Dual prefix aprovado pelo executivo:**
- `excrtx` — prefixo de skill naming (6 chars, autoexplicativo, zero colisão)
- `xc` — prefixo de slash commands (compacto para uso em gateways como Telegram)

### Taxonomia de Tipos (TYPE) — 9 categorias

| TYPE | Descrição | Escopo |
|------|-----------|--------|
| `onboard` | Onboarding e welcome flows | Primeira interação, configuração, apresentação |
| `memory` | Gestão de memória e acervo | CRUD de microversos, acervo, intake, memória operacional |
| `quality` | Qualidade de output e design system | Anti-slop, taste, quality gate, design tokens |
| `behavior` | Modos comportamentais e vetores | Vetor ativo, canvas, briefing, draft-first |
| `produce` | Produção de artefatos (execução) | Slides, ofícios, artefatos pessoais |
| `integrate` | Integrações externas (MCP, API) | Drive, NotebookLM, DocBrain, OAuth, browser |
| `govern` | Governança, aprovação, compliance | Tool governance, draft-first protocol |
| `harness` | Infraestrutura operacional | Codex core, Hermes ops, kanban, prompt log, surfaces |
| `assess` | Avaliação e diagnóstico | Self-test, repo-fit assessment |

### Regras de NAME

- Máximo 12 caracteres
- Lowercase, sem underscores (usar concatenação: `wikiadapt`, `draftfirst`)
- Descritivo da ação principal
- Sem redundância com TYPE (`excrtx-quality-quality-gate` ❌ → `excrtx-quality-gate` ✅)

### Extensibilidade

Skills de terceiros usam outro prefixo:
- `ext-{TYPE}-{NAME}` — extensões comunitárias
- `{vendor}-{TYPE}-{NAME}` — extensões de vendor específico

## Tabela de Migração Completa

| # | Nome Atual | Nome Novo | TYPE |
|---|-----------|-----------|------|
| 1 | `acervo-llm-wiki-adapter` | `excrtx-memory-wikiadapt` | memory |
| 2 | `acervo-manager` | `excrtx-memory-manager` | memory |
| 3 | `browser-use` | `excrtx-integrate-browser` | integrate |
| 4 | `codex-harness` | `excrtx-harness-core` | harness |
| 5 | `codex-integration` | `excrtx-harness-codexint` | harness |
| 6 | `codex-ops-hermes` | `excrtx-harness-hermesops` | harness |
| 7 | `docbrain-cli-api` | `excrtx-integrate-docbrain` | integrate |
| 8 | `exocortex-base-microverso-setup` | `excrtx-memory-mvsetup` | memory |
| 9 | `exocortex-briefing` | `excrtx-behavior-briefing` | behavior |
| 10 | `exocortex-canvas` | `excrtx-behavior-canvas` | behavior |
| 11 | `exocortex-design-system` | `excrtx-quality-designsys` | quality |
| 12 | `exocortex-draft-first` | `excrtx-govern-draftfirst` | govern |
| 13 | `exocortex-kanban-backlog` | `excrtx-harness-kanban` | harness |
| 14 | `exocortex-new-microverso` | `excrtx-memory-newmicro` | memory |
| 15 | `exocortex-notebooklm-knowledge-router` | `excrtx-integrate-nlmroute` | integrate |
| 16 | `exocortex-notebooklm-operational-workflow` | `excrtx-integrate-nlmops` | integrate |
| 17 | `exocortex-onboarding` | `excrtx-onboard-welcome` | onboard |
| 18 | `exocortex-operational-memory` | `excrtx-memory-opsmemory` | memory |
| 19 | `exocortex-output-quality-gate` | `excrtx-quality-gate` | quality |
| 20 | `exocortex-prompt-log` | `excrtx-harness-promptlog` | harness |
| 21 | `exocortex-self-test` | `excrtx-assess-selftest` | assess |
| 22 | `exocortex-slides` | `excrtx-produce-slides` | produce |
| 23 | `exocortex-tool-governance` | `excrtx-govern-tools` | govern |
| 24 | `exocortex-vetor-ativo` | `excrtx-behavior-vetor` | behavior |
| 25 | `gerador-oficios` | `excrtx-produce-oficios` | produce |
| 26 | `google-drive-direct-api` | `excrtx-integrate-gdrive` | integrate |
| 27 | `hermes-mcp-oauth-integrations` | `excrtx-integrate-oauth` | integrate |
| 28 | `hermes-surface-architecture` | `excrtx-harness-surfaces` | harness |
| 29 | `personal-artifact-workspace` | `excrtx-produce-artifacts` | produce |
| 30 | `personal-intake-workspace` | `excrtx-memory-intake` | memory |
| 31 | `stop-slop` | `excrtx-quality-antislop` | quality |
| 32 | `taste-skill` | `excrtx-quality-taste` | quality |
| 33 | `technical-repo-fit-assessment` | `excrtx-assess-repofit` | assess |

**Nota:** A skill #17 `exocortex-onboarding` é simultaneamente renomeada e dividida em duas (ADR-014):
- `excrtx-onboard-welcome` — apresentação + setup de gateway
- `excrtx-onboard-interview` — entrevista dos 5 blocos + geração SOUL.md

Total pós-migração: **34 skills** (33 renomeadas + 1 nova `excrtx-onboard-interview`).

## Consequências

- Autocomplete com `excrtx-` filtra todas as skills do sistema
- TYPE comunica intenção: novo agente sabe que `excrtx-quality-*` é sobre output quality sem ler SKILL.md
- Migração é destrutiva: requer atualização atômica de bundle, profiles, setup.sh, SOUL_SEED.md
- Script `migrate_skill_names.sh` automatiza o rename + atualização de referências
- Skills de terceiros ficam em namespace separado (`ext-*`)
