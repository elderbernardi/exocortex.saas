---
name: excrtx-integrate-databrain
description: Operate Projeto B DataBrain through a governed MCP control plane for health, ingestion, pipeline stages, publication and audit.
version: 1.2.0
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
- acompanhar uma operação e analisar seus logs;
- disponibilizar o Cockpit do gestor com acesso restrito via Tailscale.

## Arquitetura

A skill usa o MCP local `databrain-ops`, que adapta três superfícies canônicas:

1. API Cockpit local (`http://127.0.0.1:8000`) para saúde e histórico saneado;
2. CLI oficial dentro do container `databrain-databrain-1` para estágios sem Oracle;
3. wrapper host `/srv/databrain/ops/ingest-run.sh` para qualquer operação com `--fetch-oracle`, preservando VPN efêmera, `flock`, preflight e watermark.

Não existe ferramenta de shell livre. Toda mutação resolve para uma operação da allowlist `projetob.databrain.ops.v1`.

## Estado operacional vigente (17/11/2026)

Antes de iniciar trabalho, usar `databrain_execution_status`. Esta consulta reúne diário, semanal, últimas operações manuais da ponte e entrega de eventos; o histórico tradicional de `databrain_list_runs` não cobre a execução diária. `databrain_health` distingue disponibilidade da API e execução.

- `availability=stale|unavailable`: não declarar sucesso nem confirmar processamento; investigar observador.
- `daily.state=pending`: há obrigações remanescentes, não inferir publicação incompleta pelo código 3.
- `daily.capacity.ready=false`: a próxima tranche não pode iniciar com segurança. Preservar evidências e não reduzir a reserva de disco.
- Em evento autenticado, consultar estado atual e usar `databrain_ack_event(event_id)` após leitura disponível. Ack confirma processamento, não autorização de execução/publicação. Repetição do mesmo evento não autoriza repetir pipeline ou gasto.
- Linha histórica `stale_unconfirmed` não pode ser convertida em succeeded sem prova da unidade/processo e do resultado.

Runbook vigente: DataBrain `ops/EXECUTION_CONTROL.md`. Planos e handoffs antigos preservam decisões datadas; GO/NO-GO pertence à identidade/evidência da respectiva revisão. Gates locais via `pb heavy`; não exigir pagamento ou reativação de Actions. Não repetir campanha paga quando a identidade canônica não mudou e o verificador aceita a evidência vigente.

## Procedure

1. Chamar `databrain_health`.
2. Para ingestão, chamar `databrain_list_inbox` e reportar o inventário antes de executar.
3. Chamar `databrain_prepare_operation` com uma operação nomeada.
4. Aplicar a governança:
   - leitura e escrita local: executar diretamente;
   - Hot/Judge: informar que há custo de LLM;
   - `publish` e `incremental_publish`: apresentar DRAFT e aguardar aprovação explícita.
5. Chamar `databrain_start_operation` com o receipt exato. Para publicação, incluir `approval_ref` pós-DRAFT.
6. Consultar `databrain_operation_status` e `databrain_operation_logs` até concluir. Para Hot longo, use status como fonte de ciclo de vida e logs em intervalos mais amplos (5–10 min), evitando inundar o contexto com logs por cliente.
7. Ao concluir Hot, leia a cauda final dos logs e registre o resumo emitido pelo estágio: `clientes`, `briefings`, `insights`, `llm_calls`, tokens de entrada/saída/total, `fallbacks`, duração e a confirmação `Hot Engine Gold output written`.
8. Validar o efeito:
   - ingest/local: conferir exit code e novo run;
   - Hot: exigir `operation_status=succeeded`, `ExecMainStatus=0` e o resumo final do estágio; o status sozinho não fornece a qualidade/volume da geração;
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

### Sequenciamento ERP → Hot

Quando o executivo pedir **“ingestão ERP completa para que o Hot rode com dados atualizados”**, trate como duas etapas deliberadamente separadas:

1. Execute `incremental_refresh_prepare` quando o pedido incluir atualização integral de dimensões; ele busca Oracle, atualiza Bronze → Silver → Gold e mantém `--skip-hot --skip-publisher`.
2. Valide o run concluído, o watermark, a inbox vazia, as contagens de ingestão e a promoção Silver/Gold antes de liberar a próxima etapa.
3. Se houver Scanntech ativo, confirme nos logs o `vintageKey` selecionado e que os quatro Golds Scanntech foram regravados. A safra pode manter o mesmo timestamp de origem, mas seus cruzamentos com o ERP atualizado precisam ser recalculados.
4. Só então prepare `hot`, informe que há custo de LLM e deixe explícito que não haverá publicação. A frase “para que o Hot possa rodar” é preparatória; execute-o somente se o executivo também pedir “rode/executa o Hot” ou confirmar após a informação de custo.

Ao reportar, separe: **ERP/Gold atualizado**, **Hot ainda não executado** e **nenhuma publicação realizada**. Não use o sucesso da operação de lake como evidência de que briefings ou insights foram regenerados.

### Judge automático e escopo real do Publisher

Antes de informar custo ou qualidade do Judge, leia o resumo final dos logs. Quando `judge.auto_approve=true`, o estágio aprova administrativamente todos os itens pendentes, sem avaliação dimensional por LLM — o resumo deve mostrar `llm_calls: 0` e tokens zerados. Nesse cenário, o estágio Judge é aprovação administrativa. O Hot pode ter executado o julgamento factual semântico; confira a proveniência e as chamadas desse julgamento separadamente. Não atribua avaliação por IA ao estágio administrativo nem conclua que o Hot não usou juiz pelo contador zero do Judge externo.

No DRAFT de `publish`, não deduza contagens finais apenas da última Hot ou do Judge. O Publisher atual pode sincronizar dimensões e carteiras, expirar/gerar insights e inbox, histórico cliente×produto, preços, rankings e consolidação matriz/filial, além dos artefatos Gold/Hot/Judge. Declare o escopo como publicação ampla e liste as famílias afetadas. Depois da aprovação, só considere concluído com `operation_status=succeeded`, exit code 0, `Publisher Stage Completed` com `errors: 0` e `Publish log recorded` dos artefatos críticos.

**Inbox não é prova por lote.** Se o Publisher disser que publicou mensagens, valide a inbox pelo `vendedor_id` da conta que relatou o problema antes de atribuir a ausência ao app. Contas de teste/sombra podem ter `cliente_acesso`, briefings e insights, mas ficar fora de mensagens automáticas quando o conjunto de destinatários é derivado apenas de vendedores com `erp_ref_code`. Diferencie explicitamente persistência do lote, elegibilidade do destinatário e exibição no PWA. Procedimento e decisão de remediação em `references/inbox-delivery-verification.md`.

Detalhes e exceções recuperáveis em `references/publisher-scope-and-auto-judge.md`.

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

`publish_retry` não faz parte da v1: a flag `--retry-failed` cai em publicação completa na imagem implantada e não oferece recuperação seletiva real.

## Limites

- Nunca montar comandos a partir de texto do usuário.
- Nunca expor segredo, `.env` ou credenciais Oracle/Supabase.
- Nunca navegar diretamente em rotas brutas do Cockpit (inclusive `/cockpit/runs/{id}`) para diagnóstico. Em 2026-08-30, a rota local de detalhe devolveu `config_snapshot` sem autenticação de sessão e incluiu material sensível; use somente os outputs saneados do MCP. Se esse vazamento for observado, não reproduza valores: registre incidente de segurança, preserve apenas evidência não sensível e proponha rotação/restrição via DRAFT.
- Nunca rodar duas operações da ponte em paralelo.
- Nunca contornar `approval_ref` em escrita externa.
- Nunca interpretar `started` como sucesso; aguardar `succeeded` e exit code 0.
- Nunca usar a cópia aposentada `databrain.clean.RETIRED-*`.

## Pitfalls

- **Imagem versus checkout:** a produção executa a imagem do container, não a working tree local; sempre usar o CLI dentro de `databrain-databrain-1`.
- **Started não é sucesso:** iniciar uma unidade só prova aceitação; aguardar `succeeded` e `ExecMainStatus=0`.
- **Política factual vigente:** no perfil `semantic-v1`, heurísticas de frases/cifras/verbos, densidade numérica e estilo são diagnósticos. Todo texto utilizável passa pelo juiz factual; incerteza é pendência, e descarte factual exige contradição comprovada. Não converter alertas antigos de estilo em NO-GO nem alegar que foram descartes corretos na política atual. `legacy-strict` permanece apenas para reprodução explícita do protocolo histórico. Conferir proveniência, texto final julgado e resultado real da operação.
- **Operação concorrente:** advisory locks internos protegem o pipeline, mas a ponte também bloqueia dois starts simultâneos.
- **Dados externos:** toda operação Oracle usa `/srv/databrain/ops/ingest-run.sh`; nunca substituir por `docker exec`, pois o wrapper governa VPN exclusiva, `flock`, preflight e watermark.
- **Scheduler:** os timers host `databrain-ingest.timer` (semanal) e `databrain-insights-daily.timer` (diário seletivo) são canônicos; o scheduler interno do container fica desligado para evitar duplicidade.
- **Publicação:** `publish*` muda Supabase/Sales-AI e sempre exige DRAFT pós-intenção + `approval_ref`.
- **Cópia aposentada:** nunca usar `databrain.clean.RETIRED-*`.
- **`dry_run` valida orquestração, não mapeamento de arquivo:** o dry-run termina `succeeded` com `stages: []` e counts zerados mesmo com um arquivo novo na inbox — ele valida o plano do pipeline, não se o schema Bronze aceita o formato. Para provar compatibilidade de um arquivo externo, é preciso rodar `ingest_inbox` (Bronze local, reversível). Nunca usar dry_run como green para ingestão.
- **Inbox física exige sudo:** a inbox de produção fica em `/srv/databrain/data/inbox` (grupo `databrain`, `drwxr-x---`); o MCP lista via `sudo -n find`. Para copiar um arquivo externo, usar `sudo -n cp` + `sudo -n sha256sum` para verificar; nome na inbox deve ser limpo (sem prefixos de cache). Procedimento completo em `references/external-file-ingestion.md`.
- **Exposição Tailscale:** auditar credenciais e JWT antes de qualquer `tailscale serve`; a presença de fallback de desenvolvimento bloqueia a exposição. Usar proxy loopback allowlisted e nunca Funnel. O perfil mínimo é o default; ampliar para APIs gerenciais e runs exige DRAFT próprio, enumeração de rotas/métodos e autenticação adicional no proxy. Validar separadamente disponibilidade da API e presença de telas na UI — resposta `200` não prova que o gestor consegue usar a função visualmente. Consulte `references/tailscale-cockpit-exposure.md`.

## Gate de promoção Scanntech

Após uma ingestão Scanntech bem-sucedida, não presuma que a safra chegou ao produto publicável. Antes de Hot, Judge ou Publisher, valide a cadeia inteira:

1. **Bronze:** existem os três Parquets mais recentes (`geral`, `guimaraes`, `share`) com timestamp da safra recebida.
2. **Silver:** `dim_pdv_scanntech` e `fact_mercado_scanntech` foram regravados depois da Bronze correspondente.
3. **Gold:** os quatro artefatos Scanntech — `share_overlap`, `prospects_alta_prioridade`, `alertas_queda_share` e `ranking_compradores` — foram regravados depois da Silver.
4. Somente então execute Hot/Judge e apresente o DRAFT de publicação.

Código de saída `0` de uma etapa isolada não substitui a prova de promoção entre camadas. Se timestamps ou artefatos não avançarem, interrompa a cadeia: não rode Hot/Judge e não publique dados potencialmente anteriores. Abra diagnóstico da transição Bronze → Silver/Gold com logs e evidência de artefato antes de qualquer correção.

## Verification

- `hermes mcp test databrain-ops` conecta e descobre 9 tools.
- `databrain_health` retorna API `ok`, container `healthy`, timer canônico do host e scheduler interno desligado.
- `dry_run` termina com status `succeeded` e exit code 0.
- tentativa de `publish` sem `approval_ref` é recusada.

## Referência operacional

Para diagnóstico de deploy, escolha do executor, scheduler host versus interno, sanitização, recovery e isolamento por worktree, consulte `references/deployment-and-control-plane-verification.md`.

Para publicar o Cockpit do gestor no tailnet com proxy restritivo, auditoria prévia de credenciais, bloqueio de rotas técnicas e verificação sem Funnel, consulte `references/tailscale-cockpit-exposure.md`.

Para ingerir arquivos externos (planilhas, CSVs, exports de fornecedores) na inbox de produção, verificação de integridade e limites do dry_run, consulte `references/external-file-ingestion.md`.
