---
name: excrtx-integrate-databrain
description: Operate Projeto B DataBrain through a governed MCP control plane for health, ingestion, pipeline stages, publication and audit.
version: 1.0.0
category: excrtx
platforms:
  - linux
metadata:
  hermes:
    tags:
      - exocortex
      - databrain
      - projetob
      - mcp
      - operations
    related_skills:
      - excrtx-integrate-mcp
      - excrtx-govern-draftfirst
      - excrtx-sales-ai-analysis
---

# DataBrain — Ponte Operacional Governada

## When to Use

Ative quando o executivo pedir para operar o DataBrain do Projeto B:
- verificar saúde ou histórico;
- inspecionar a inbox de ingestão;
- ingerir arquivos;
- buscar o incremental do Sankhya/Oracle;
- executar Cold, Hot, Judge ou Publisher;
- acompanhar uma operação e analisar seus logs.

## Arquitetura

A skill usa o MCP local `databrain-ops`, que adapta duas superfícies canônicas:

1. API Cockpit local (`http://127.0.0.1:8000`) para saúde e histórico;
2. CLI oficial dentro do container `databrain-databrain-1` para execução.

Não existe ferramenta de shell livre. Toda mutação resolve para uma operação da allowlist `projetob.databrain.ops.v1`.

## Procedure

1. Chamar `databrain_health`.
2. Para ingestão, chamar `databrain_list_inbox` e reportar o inventário antes de executar.
3. Chamar `databrain_prepare_operation` com uma operação nomeada.
4. Aplicar a governança:
   - leitura e escrita local: executar diretamente;
   - Hot/Judge: informar que há custo de LLM;
   - `publish`, `publish_retry` e `incremental_publish`: apresentar DRAFT e aguardar aprovação explícita.
5. Chamar `databrain_start_operation` com o receipt exato. Para publicação, incluir `approval_ref` pós-DRAFT.
6. Consultar `databrain_operation_status` e `databrain_operation_logs` até concluir.
7. Validar o efeito:
   - ingest/local: conferir exit code e novo run;
   - publicação: conferir run + Sales-AI somente após sucesso.

## Comandos naturais suportados

O executivo pode pedir, em PT-BR:

- **“Verifique a saúde do DataBrain.”** → saúde da API, container, último pipeline e scheduler.
- **“Liste as últimas execuções do DataBrain.”** → histórico do Cockpit saneado.
- **“O que está aguardando ingestão?”** → inventário da inbox, sem ler conteúdo.
- **“Valide o pipeline do DataBrain.”** → `dry_run`.
- **“Faça a ingestão dos arquivos da inbox.”** → inventário, receipt, `ingest_inbox` e acompanhamento.
- **“Atualize os dados do Sankhya sem IA nem publicação.”** → `incremental_prepare`.
- **“Atualize dimensões e dados sem publicar.”** → `incremental_refresh_prepare`.
- **“Atualize os dados e gere a IA, sem publicar.”** → `incremental_ai_prepare`.
- **“Prepare a publicação dos dados atuais.”** → DRAFT de `publish`; só executa após aprovação posterior.
- **“Rode a atualização completa e publique.”** → DRAFT de `incremental_publish`; só executa após aprovação posterior.
- **“Acompanhe a operação `<id>`.”** → status + logs até conclusão.

Pedidos de “atualizar dados” sem explicitar IA/publicação devem usar o default conservador `incremental_prepare`. Nunca interpretar “ingerir” como autorização para publicar.

## Operações v1

| Operação | Efeito | Gate |
|---|---|---|
| `dry_run` | validação | direto |
| `ingest_inbox` | Bronze local | inventário antes |
| `cold` | lake local | direto |
| `hot` | lake + LLM | informar custo |
| `judge` | quarentena + LLM | informar custo |
| `incremental_prepare` | Oracle → Gold, sem LLM/publicação | direto |
| `incremental_refresh_prepare` | Oracle + refresh dims → Gold | direto |
| `incremental_ai_prepare` | Oracle → Judge, sem publicação | informar custo |
| `incremental_publish` | pipeline completo → Sales-AI | DRAFT obrigatório |
| `publish` | Gold atual → Sales-AI | DRAFT obrigatório |
| `publish_retry` | retry de falhas → Sales-AI | DRAFT obrigatório |

## Limites

- Nunca montar comandos a partir de texto do usuário.
- Nunca expor segredo, `.env` ou credenciais Oracle/Supabase.
- Nunca rodar duas operações da ponte em paralelo.
- Nunca contornar `approval_ref` em escrita externa.
- Nunca interpretar `started` como sucesso; aguardar `succeeded` e exit code 0.
- Nunca usar a cópia aposentada `databrain.clean.RETIRED-*`.

## Pitfalls

- **Imagem versus checkout:** a produção executa a imagem do container, não a working tree local; sempre usar o CLI dentro de `databrain-databrain-1`.
- **Started não é sucesso:** iniciar uma unidade só prova aceitação; aguardar `succeeded` e `ExecMainStatus=0`.
- **Operação concorrente:** advisory locks internos protegem o pipeline, mas a ponte também bloqueia dois starts simultâneos.
- **Dados externos:** `incremental_prepare` lê Oracle via VPN; falha de VPN deve ser reportada, não contornada.
- **Publicação:** `publish*` muda Supabase/Sales-AI e sempre exige DRAFT pós-intenção + `approval_ref`.
- **Cópia aposentada:** nunca usar `databrain.clean.RETIRED-*`.

## Verification

- `hermes mcp test databrain-ops` conecta e descobre 9 tools.
- `databrain_health` retorna API `ok`, container `healthy` e o estado efetivo do scheduler lido de `DATABRAIN_SCHEDULER_ENABLED`.
- `dry_run` termina com status `succeeded` e exit code 0.
- tentativa de `publish` sem `approval_ref` é recusada.
