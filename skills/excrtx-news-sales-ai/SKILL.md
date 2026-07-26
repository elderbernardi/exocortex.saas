---
name: excrtx-news-sales-ai
description: Use when Exocórtex must run the Route B news workflow for Sales-AI — research and curate signals, build a publishable dossier, and hand off publication to the canonical Sales-AI writer while keeping DataBrain as an on-demand harness only.
version: 1.0.0
category: excrtx
platforms: [linux]
author: Exocórtex
license: MIT
metadata:
  hermes:
    tags: [exocortex, news, sales-ai, route-b, databrain, docbrain]
    related_skills: [excrtx-integrate-docbrain, excrtx-crawler-brasil, excrtx-research-cpg-brasil, excrtx-govern-draftfirst]
compiled_rules: |
  # This skill does not inject runtime rules; it is a tool-only skill.
  # v1 default: Modo A (cron autônomo) publica sem subir o harness DataBrain e
  # sem DocBrain (use_docbrain=false); Modo B (manual) segue o mesmo default.
  # Guard read-before-write nunca reativa uma notícia com ativo=false —
  # Camada 2, complementar ao writer publish_noticia v3.1.0 (skipped_retired).
---
# excrtx-news-sales-ai

## Overview

Esta skill materializa a **Rota B** do pipeline de notícias.

O agente Exocórtex pesquisa, consolida sinais, contextualiza documentos e prepara a curadoria. O **DataBrain não roda como processo ativo** para notícias: ele fica restrito a contratos, contexto, targets, guard, ledger, receipts e expire-plan, sob demanda. A publicação canônica continua no **Sales-AI MCP**.

O objetivo da skill é reduzir improviso operacional. Ela define a fronteira, a sequência de execução e o artefato intermediário que permite curadoria governada antes do publish.

## Modos de operação

Esta skill tem dois modos. O runbook Route B abaixo (harness DataBrain sob demanda,
DocBrain como contexto) permanece **válido e opcional** — nenhum foi removido.

### Modo A — autônomo (cron, macro)
Dirigido por `config/noticias.toml`. Um cron despachante decide quais áreas rodam:

1. `python3 scripts/news_dispatch.py --config config/noticias.toml --state <acervo>/news-cadence.json --now $(date +%s)` → lista de áreas vencidas.
2. Para cada área: `python3 ../excrtx-research-cpg-brasil/scripts/orchestrate.py --template <slug> --output json --skip-l30d` (sem `--document`; `use_docbrain=false`).
3. `python3 scripts/build_dossier.py --job-context <ctx.json> --crawler <research.json> --agent-reach <research.json> --output-file <dossier.json>` (reusa os itens brutos por canal do helper; **não** passar `--docbrain`).
4. Curadoria com o modelo a partir do `prompt_packet`: dedup, relevância ≥ `relevance_threshold`, `impacto`, headline via `excrtx-quality-antislop`, **só itens com url/fonte reais**; cap `max_items`.
5. Guard: `partition()` de `scripts/news_guard.py` (via `fetch_existing`) descarta url já ativa/retirada.
6. Publicar cada item do bucket `publish` via MCP `publish_noticia` (escopo=macro); tratar `resultado ∈ {created, updated, skipped_retired}`.
7. `python3 scripts/news_dispatch.py --config config/noticias.toml --state <acervo>/news-cadence.json --mark <slug> --now $(date +%s)` para carimbar o run.
8. Expirar vencidos via MCP `expire_noticia`.

### Modo B — manual (comercial/gestão, via agente)
Quando comercial ou gestão pede para publicar uma notícia específica:
1. Receber título, url (**obrigatória**), fonte, impacto (headline opcional).
2. Passar a headline por `excrtx-quality-antislop`.
3. Guard `partition()` de 1 item (não reativa retirada).
4. `publish_noticia` com `origem` = quem pediu (`comercial`/`gestao`). Sem pesquisa/curadoria.

## When to Use

Use quando:
- o executivo pedir para rodar o pipeline de notícias na arquitetura Route B;
- o agente precisar preparar uma leva macro ou micro de notícias para o Sales-AI;
- o DataBrain tiver ingerido dados e precisar pedir prospecção/publicação ao agente em tempo de execução;
- você precisar consolidar sinais de crawler, Agent-Reach e DocBrain antes da curadoria final.

**Don't use for:** publicar direto sem contexto, usar o DataBrain como processo ativo, ou empurrar coleta RSS/LLM para dentro do DataBrain.

## Arquitetura operacional

```text
Hermes / Exocórtex
  ├─ coleta sinais externos
  │   ├─ excrtx-crawler-brasil
  │   ├─ Agent-Reach / last30days (quando fizer sentido)
  │   └─ DocBrain para documentos locais
  ├─ monta dossier determinístico
  ├─ faz curadoria com modelo
  ├─ pede guard/harness ao DataBrain sob demanda
  └─ publica pelo writer canônico do Sales-AI MCP

DataBrain
  └─ contratos + contexto + targets + guard + ledger + receipts + expire-plan

Sales-AI MCP
  ├─ publish_noticia
  └─ expire_noticia
```

## Fronteira obrigatória

> **v1 autônomo (default):** o Modo A **não** usa o harness DataBrain nem DocBrain
> (publica sem DataBrain up; `use_docbrain=false`). As etapas de harness/DocBrain
> abaixo continuam disponíveis para o runbook manual/avançado, mas são **opcionais**.

### Fica no Exocórtex
- pesquisa e coleta;
- adaptação de fontes;
- uso de DocBrain em documentos;
- consolidação de sinais em dossier;
- curadoria editorial;
- decisão de macro vs micro;
- handoff para publicação.

### Fica no DataBrain
- `news-job-context`;
- targets de carteira;
- guard e validação final do lote;
- ledger / receipts / expire-plan;
- contratos versionados.

### Fica no Sales-AI MCP
- escrita canônica em `noticias_publicas`;
- expiração/retirada canônica.

## Procedure

1. **Resolver o modo do job**
   - Defina se o trabalho é `macro` ou `micro`.
   - Para `micro`, confirme `cliente_id` e nome público do cliente.
   - Critério de conclusão: existe um `news-job-context` válido ou um plano explícito para gerá-lo via DataBrain.

2. **Obter o contexto e targets sem subir o DataBrain como processo**
   - Use o harness CLI do DataBrain, sob demanda, para gerar contexto e targets.
   - Fluxo preferido:
     ```bash
     databrain news context --scope macro --output /tmp/news-context.json
     databrain news targets --seller-id <uuid> --output /tmp/news-targets.json
     ```
   - Critério de conclusão: há um `news-job-context` local em JSON e, quando aplicável, uma lista de targets priorizados.

3. **Coletar sinais externos**
   - Use `excrtx-crawler-brasil` como base setorial brasileira.
   - Use Agent-Reach e/ou last30days só quando ampliarem a cobertura.
   - Use DocBrain para anexos, PDFs, dossiês e material local de suporte.
   - Critério de conclusão: cada fonte relevante gerou JSON local auditável.

4. **Montar o dossier determinístico**
   - Use o helper desta skill:
     ```bash
     python3 skills/excrtx-news-sales-ai/scripts/build_dossier.py \
       --job-context /tmp/news-context.json \
       --crawler /tmp/crawler.json \
       --agent-reach /tmp/agent-reach.json \
       --docbrain /tmp/docbrain.json \
       --output pretty \
       --output-file /tmp/news-dossier.json
     ```
   - O dossier normaliza sinais, remove duplicatas óbvias e produz um `prompt_packet` compatível com a curadoria.
   - Critério de conclusão: existe um dossier com schema `exocortex/news-route-b-dossier/v1`.

5. **Curar candidatos com o modelo**
   - Use o `prompt_packet` do dossier para produzir candidatos com justificativa curta, sem publicar ainda.
   - Regras duras:
     - não inventar evidência;
     - `micro` exige ligação explícita com o cliente-alvo;
     - documento DocBrain complementa contexto, não substitui notícia pública.
   - Critério de conclusão: existe um conjunto de candidatos revisáveis, separado entre publicar / revisar / rejeitar.

6. **Passar no guard do DataBrain**
   - O lote final deve ser validado pelo harness antes do publish.
   - Fluxo preferido:
     ```bash
     databrain news guard --input /tmp/candidates.json --output /tmp/news-batch.json --scope macro
     ```
   - Critério de conclusão: existe `news-batch` canônico pronto para writer e o lote rejeitado/revisão foi preservado para auditoria.

7. **Publicar pelo Sales-AI MCP**
   - Writer canônico: `publish_noticia`.
   - Para micro notícia, `cliente_id` é obrigatório.
   - Depois do publish, registre receipts e atualize o ledger via harness do DataBrain.
   - Critério de conclusão: cada publicação tem receipt normalizado e o run foi finalizado no ledger.

8. **Planejar expiração**
   - Gere o expire-plan no DataBrain e use o Sales-AI MCP para retiradas canônicas quando necessário.
   - Critério de conclusão: itens vencidos ou superados têm plano de expiração gerado e auditável.

## Helper incluído

### `scripts/build_dossier.py`

Função: consolidar JSONs já coletados em um dossier determinístico para curadoria.

Entradas:
- `--job-context` (obrigatório)
- `--crawler` (0..N)
- `--agent-reach` (0..N)
- `--docbrain` (0..N)
- `--max-signals`
- `--output-file`

Saída:
- `schema: exocortex/news-route-b-dossier/v1`
- `focus`
- `job_context`
- `source_counts`
- `signals`
- `documents`
- `prompt_packet`

## Contratos relevantes

- `projetob/news-job-context/v1`
- `projetob/news-batch/v1`
- writer canônico Sales-AI: `publish_noticia`
- expiração canônica Sales-AI: `expire_noticia`

## Common Pitfalls

1. **Subir o DataBrain como worker de notícias**
   - Errado. DataBrain é harness on-demand; não runtime ativo da Rota B.

2. **Publicar antes do guard**
   - A skill pode coletar e curar, mas a validação final do lote continua no harness (no runbook Route B/harness; no Modo A/B a validação é o guard local `news_guard.py`).

3. **Tratar DocBrain como fonte de notícia pública**
   - Documento local entra como contexto estruturado, não como substituto de matéria pública.

4. **Misturar macro e micro no mesmo lote sem fronteira explícita**
   - Cada lote precisa de `scope` claro e, para micro, `cliente_id` explícito.

5. **Perder receipts**
   - Publicação sem receipt/ledger enfraquece auditoria e expiração posterior.

6. **Usar o dossier como artefato final**
   - O dossier prepara curadoria. O lote canônico de publish é o `news-batch` guardado pelo DataBrain.

## Verification Checklist

- [ ] `SKILL.md` tem frontmatter válido e seções obrigatórias
- [ ] `python3 skills/excrtx-news-sales-ai/scripts/build_dossier.py --help` retorna exit 0
- [ ] O helper gera JSON com schema `exocortex/news-route-b-dossier/v1`
- [ ] O dossier contém `prompt_packet` com writer contract e harness contract
- [ ] Fluxo documenta explicitamente que DataBrain não é processo ativo de notícias
- [ ] Publicação está roteada para o writer canônico Sales-AI, não para código local
- [ ] O guard/harness do DataBrain aparece como etapa obrigatória antes do publish

## References and Files

- `references/route-b-architecture.md`
- `scripts/build_dossier.py`
- Skill irmã: `excrtx-integrate-docbrain`
- Skill irmã: `excrtx-crawler-brasil`
- Skill irmã: `excrtx-research-cpg-brasil`
