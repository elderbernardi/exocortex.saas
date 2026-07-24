# Route B — arquitetura operacional de notícias

## Princípio

O sistema de publicação de notícias deve funcionar **sem o DataBrain ativo como processo**.

Isso não elimina o DataBrain. Rebaixa o papel dele para **harness determinístico**:
- contratos;
- contexto;
- targets;
- guard;
- ledger;
- receipts;
- expire-plan.

A inteligência ativa fica no Exocórtex.

## Fluxo

```text
1. DataBrain gera ou expõe contexto/targets sob demanda
2. Exocórtex coleta sinais (crawler / Agent-Reach / DocBrain)
3. Exocórtex consolida tudo num dossier determinístico
4. Exocórtex faz curadoria com modelo
5. DataBrain valida o lote final (guard)
6. Sales-AI MCP publica canonicamente
7. DataBrain registra receipts / ledger / expire-plan
```

## Separação de responsabilidade

### Exocórtex
- pesquisa e prospecção;
- ingestão documental;
- adaptação de fontes;
- normalização ativa do trabalho do agente;
- curadoria;
- decisão editorial;
- handoff para publish.

### DataBrain
- não é crawler;
- não é curador;
- não é scheduler de notícias;
- não é processo worker do pipeline;
- é plano de controle e superfície determinística.

### Sales-AI MCP
- único writer canônico;
- única expiração canônica.

## Artefatos recomendados

### Antes da curadoria
- `news-job-context.json`
- `news-targets.json` (quando micro)
- `crawler.json`
- `agent-reach.json`
- `docbrain.json`
- `news-dossier.json`

### Antes do publish
- `candidates.json`
- `news-batch.json`

### Depois do publish
- `receipts.json`
- `expire-actions.json`

## Regra de governança

A skill pode preparar e organizar tudo localmente.

A publicação só é considerada pronta quando:
1. o lote passou no guard do DataBrain;
2. o writer canônico do Sales-AI respondeu;
3. receipts foram registrados.
