---
type: decision
title: 'ADR: DocBrain não é público — referências em superfícies públicas são vazamento'
description: '**Data:** 2026-06-17'
tags: []
timestamp: 2026-06-19
class: perene
created_at: 2026-06-19T22:34:48Z
last_accessed_at: 2026-06-19T22:34:48Z
---

# ADR: DocBrain não é público — referências em superfícies públicas são vazamento

**Data:** 2026-06-17
**Status:** IDENTIFICADO — remediação pendente

## Contexto

DocBrain (`github.com/ProjetoBB/docBrainBB.git`) é um repositório privado. O setup do Exocórtex referencia DocBrain em múltiplas superfícies públicas que qualquer usuário externo pode ver ao rodar o instalador ou ler a README.

## Superfícies afetadas

1. **README.md** — catálogo de skills (EX-27), seção "Full Installation" (`DOCBRAIN_LLM_API_KEY`), descrição de steps, seção "5. DocBrain Parser Engine Setup" inteira com instruções de clone e build
2. **install.sh** — preflight de env vars lista `DOCBRAIN_LLM_API_KEY` (linha 64 e 217 — números possivelmente desatualizados; verificar no arquivo atual)
3. **setup/step-08-integration-docbrain.sh** — clona o repo privado diretamente; falha para qualquer usuário externo
4. **skills/excrtx-integrate-docbrain/** — skill inteira referenciando DocBrain

## Impacto

Usuário externo que roda `curl | bash` vê:
- Nome "DocBrain" na narrativa de instalação
- Referência a `DOCBRAIN_LLM_API_KEY` no preflight
- Tentativa de clone de repo privado (que falha silenciosamente)
- Seção completa na README com passos de setup

## Opções de remediação (a decidir)

- **A) Remover DocBrain de toda superfície pública** — README, install.sh preflight, step-08. Skill fica no repo mas setup não clona automaticamente.
- **B) Gated por env var** — step-08 só executa se `EXOCORTEX_ENABLE_DOCBRAIN=1`. DocBrain sai da "full install" da README.
- **C) Remover DocBrain completamente do repo** — skill, step, referências.

## Nota

Tag v1.0.1 já publicada no remote inclui as referências na README. Remediação requer novo commit + push + atualização de tag.

## Atualização factual (config de LLM consolidada em 3 papéis)

> Esta nota apenas corrige referências factualmente desatualizadas; a decisão e
> o raciocínio histórico acima permanecem inalterados.

A `DOCBRAIN_LLM_API_KEY` deixou de ser uma var de provider configurada
diretamente. A config de LLM foi consolidada em 3 papéis e o `.env` do DocBrain
agora é gerado a partir do papel **auxiliar** (`EXOCORTEX_AUX_*`): o
`setup/step-08-integration-docbrain.sh` escreve a `DOCBRAIN_LLM_API_KEY` do
DocBrain derivada do papel aux. A var legada foi migrada uma única vez por
`scripts/migrate-env-roles.py`.
