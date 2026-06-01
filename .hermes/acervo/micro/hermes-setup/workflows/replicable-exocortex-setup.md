
---
title: Workflow — Setup Replicável do Exocórtex
created: 2026-05-30
updated: 2026-06-01
nature: processos
kind: workflow
scope_mode: micro
scope_slug: hermes-setup
applies_to: [global]
authority: canonical
operational_mode: executable
stability: active
sources: [~/.hermes/setup.sh, plugins/memory/hindsight/README.md]
derived_from: [ontology-v2-migration]
confidence: high
promotion_policy: candidate-global
upstream:
  source_skill: autonomous-ai-agents/hermes-agent
  assumed_version: null
  coupling: adapter-only
tags: [setup, replicability, hermes, exocortex]
---

# Workflow — Setup Replicável do Exocórtex

0. Separar runtime e workspace:
   - `HERMES_HOME=~/.hermes` para config, auth, sessões, logs, skills e profiles.
   - `EXOCORTEX_HOME=~/exocortex` para o cockpit cognitivo.
   - `ACERVO=~/exocortex/acervo` como fonte canônica.
   - Produção Hermes deve rodar com cwd em `~/exocortex`.
   - `~/.hermes/acervo` pode existir apenas como symlink de compatibilidade.
1. Criar as 4 camadas do Acervo em `$ACERVO`.
2. Criar diretórios funcionais v2 em `global/`, `shared/`, `_template/` e microversos base.
3. Instalar skills do bundle Exocórtex em `$HERMES_HOME/skills/exocortex`.
4. Validar `acervo-manager` e `acervo-llm-wiki-adapter`.
5. Verificar profiles `exec` e `evol`.
6. Rodar lint estrutural.
7. Para entrada, instalar o Personal Intake Workspace: `_inbox/`, contrato, ferramenta `intake_ingest.py`, skill e documentação do microverso `hermes-setup`.
8. Para artefatos finais, usar o Personal Artifact Workspace: pacote em `_artifacts/`, exports no Drive privado, manifest/receipt no Acervo e Draft-First para compartilhamento externo.
9. Para memória operacional, instalar Hindsight como provider auxiliar e opcional:
   - manter o Acervo Cognitivo v2 como fonte canônica;
   - aplicar o contrato `contracts/hindsight-operational-memory-contract.md`;
   - usar os workflows `workflows/hindsight-operational-memory.md` e `workflows/hindsight-local-docker-single-node.md`;
   - provisionar Hindsight local em `~/.hermes/hindsight-local` (Docker único) com volume persistente em `~/.hermes/hindsight-local/data`;
   - copiar o template `templates/hindsight-config.local_embedded.json` para `~/.hermes/hindsight/config.json` quando a instalação usar `local_embedded`;
   - sincronizar `llm_model` e `llm_base_url` com as mesmas configurações de LLM do setup Hermes;
   - configurar `memory.provider=hindsight` somente com ativação explícita via `EXOCORTEX_ENABLE_HINDSIGHT=1` e depois de remover placeholders `CHANGE_ME`;
   - desativar memória simples local após ativação (`memory.memory_enabled=false` e `memory.user_profile_enabled=false`);
   - usar bank único por Hermes (`bank_id_template=exocortex`), com compartilhamento entre perfis `exec`/`evol`;
   - excluir memória local apenas com confirmação explícita por parâmetros de reset;
   - iniciar conservador: `recall_types=observation`, `recall_budget=low`, `recall_max_tokens=1200`, `retain_every_n_turns=2`;
   - validar com `hermes memory status`;
   - auditar ruído, latência e utilidade após 7 e 14 dias.
10. Para intake documental, instalar DocBrain como parser engine local:
   - clonar `https://github.com/ProjetoBB/docBrainBB.git` em `${EXOCORTEX_DOCBRAIN_DIR:-$HOME/projetos/pessoal/projetob/docbrain}`;
   - rodar `npm install` e `npm run build`;
   - usar a key main do Hermes via `OPENROUTER_API_KEY`;
   - usar `DOCBRAIN_LLM_API_KEY` apenas como override explícito;
   - sem key, criar lembrete em `~/.hermes/reminders/docbrain-llm-key.md` e não bloquear setup;
   - validar com `npm run --silent cli -- api health --output json`;
   - operar pelo workflow `workflows/install-docbrain-parser-engine.md` e pela ferramenta `tools/docbrain-cli-api.md`.
11. Provisionar o microverso base `estudio-criativo`:
   - criar `micro/estudio-criativo/` com Ontologia Multifocal v2;
   - manter o núcleo genérico, adaptável ao usuário e sem contexto pessoal ou institucional;
   - incluir contratos de briefing, pesquisa antes de produção, crítica criativa, Draft-First e governança de ferramentas/skills;
   - documentar atuação própria e apoio misto com outros microversos;
   - permitir stack criativa com IA e sem IA, com instalação apenas mediante aprovação explícita quando modificar ambiente.
