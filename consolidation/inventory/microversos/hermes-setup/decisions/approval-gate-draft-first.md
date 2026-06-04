---
title: Decisão proposta — Approval-gate Draft-First no harness Exocórtex sobre Hermes
created: 2026-06-01
updated: 2026-06-01
nature: conhecimento
kind: decision
scope_mode: micro
scope_slug: hermes-setup
applies_to: [global, exocortex, hermes, gateway, cron, background]
authority: canonical
operational_mode: advisory
stability: draft
sources: [conversation:2026-06-01]
derived_from: [draft-first-drift-analysis, approval-binding-discussion]
confidence: medium
promotion_policy: candidate-global
upstream:
  source_skill: null
  assumed_version: null
  coupling: none
tags: [draft-first, approval-gate, harness, deployment, gateway]
---

# Decisão proposta — Approval-gate Draft-First no harness Exocórtex sobre Hermes

## Status

Proposta.

## Problema

O Draft-First hoje depende mais de disciplina textual do que de enforcement operacional. Isso permite drift entre o draft aprovado e a ação realmente emitida. O risco cresce quando o runtime opera com múltiplos canais, background jobs, cron, geração de links, anexos e fluxos que atravessam staging privado antes de tocar o mundo externo.

## Decisão proposta

Introduzir um approval-gate transacional no harness do Exocórtex, posicionado na fronteira entre produção interna e emissão externa.

A aprovação humana deve ficar vinculada ao payload exato do draft por fingerprint. Se qualquer campo material mudar, a aprovação expira.

Campos mínimos do fingerprint:
- canal de saída
- destinatário
- assunto ou título, quando existir
- corpo normalizado
- anexos ou links emitidos
- classificação do efeito externo

## Fronteira operacional

O sistema passa a separar dois domínios:

1. Produção interna permitida sem aprovação adicional:
- pesquisa
- síntese
- escrita local
- geração de artefatos
- upload privado de staging controlado
- receipts e manifests
- preparação de mensagens, convites, commits ou publicações como draft

2. Emissão externa bloqueada por approval-gate:
- envio de email ou mensagem
- publicação em canal, rede ou documento compartilhado
- criação ou alteração de evento de calendário
- commit, push, merge, deploy
- compartilhamento com terceiros ou abertura de permissão pública

## Modelo proposto

```text
executor interno
  -> produz artefato/draft
  -> registra fingerprint + receipt local
  -> estado = draft_ready
  -> aguarda aprovação humana explícita
  -> revalida fingerprint
  -> emite efeito externo
  -> registra receipt final
```

## Alternativas consideradas

### A. Manter enforcement só por prompt

Rejeitada. Regra textual não cria vínculo transacional entre aprovação e payload final.

### B. Bloquear toda automação externa, inclusive staging privado

Rejeitada. Isso quebra fluxos longos, cron e produção interna legítima. O problema está na emissão externa, não na preparação local.

### C. Approval-gate só no gateway de mensagens

Insuficiente. O mesmo risco aparece em email, calendário, Drive compartilhado, commits e deploys. O gate precisa nascer no harness, com taxonomia comum de side effects.

## Consequências

Positivas:
- reduz drift entre intenção, draft aprovado e ação emitida
- preserva autonomia de background jobs até a fronteira correta
- cria trilha auditável por receipt, fingerprint e estado
- permite testes adversariais sobre canais e tipos de side effect

Custos e trade-offs:
- aumenta complexidade do harness
- exige ledger local de drafts, aprovações e receipts
- pede taxonomia clara de side effects por ferramenta
- força desenho explícito para cron e tarefas assíncronas sem humano presente

## Impacto em cron e background jobs

Cron e tarefas longas continuam produzindo internamente. O run não deve travar no meio esperando conversa interativa. Em vez disso, ele deve concluir em estado `draft_ready`, com artefato verificável e pendência de aprovação para a etapa externa.

Na prática:
- cron pode coletar, resumir, montar arquivos e preparar mensagem
- cron não publica externamente sem aprovação vinculada ao draft específico
- background job pode subir material para staging privado quando isso não equivaler a compartilhamento externo

## Impacto na implantação do Exocórtex sobre Hermes

A proposta reforça a arquitetura USER -> GUI -> SERVER -> HERMES.

Implicações:
- o approval-gate deve viver no plano de execução do Exocórtex, não apenas na interface
- a GUI pode coletar aprovação, mas o SERVER ou o harness precisa validar fingerprint e estado antes da emissão
- a implantação deve preservar área privada de staging, receipts e ledger fora dos canais públicos
- a identidade Exocórtex precisa permanecer acima do runtime Hermes, com o gate modelado como política operacional do Exocórtex sobre a infraestrutura Hermes

## Decisões ainda abertas

- o gate entra como plugin do Hermes, camada do server ou combinação dos dois
- onde persistir o ledger de aprovação e seus receipts
- qual conjunto mínimo de ferramentas entra na taxonomia de side effects na primeira versão
- como expor a fila de drafts pendentes para revisão humana sem degradar a UX

## Critério de aceite para seguir para implementação

A proposta só deve avançar para implementação quando houver definição explícita de:
- ponto de interceptação
- formato do fingerprint
- máquina de estados do draft
- política para cron e background
- armazenamento auditável de receipts
