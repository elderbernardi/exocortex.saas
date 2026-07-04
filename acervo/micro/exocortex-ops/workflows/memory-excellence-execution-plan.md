---
schema: acervo/v0.2
type: workflow
title: Plano de Execução — Memória Excelente, Econômica, Contextual e Manejável
description: Plano executável para reformar a memória do Exocórtex com Hindsight, Acervo, SOUL e agentes menores.
tags: [memory, execution-plan, hindsight, acervo, agents]
timestamp: 2026-06-21
class: perene
status: active
created_at: 2026-06-21T16:37:51Z
nature: workflows
excrtx_type: workflow
confidence: high
canonical_from: micro/exocortex-dev/workflows/memory-excellence-execution-plan.md
promoted_at: 2026-06-21T21:50:00Z
scope_slug: exocortex-ops
absorbed_from: micro/exocortex-dev/workflows/memory-excellence-execution-plan.md
---

# Plano de Execução — Memória Excelente, Econômica, Contextual e Manejável

## Tese

A memória excelente do Exocórtex precisa de quatro propriedades:

1. **Econômica** — pouco contexto fixo no prompt.
2. **Contextual** — recupera informação certa para a tarefa certa.
3. **Canônica** — decisões e conhecimento vivem no Acervo, não em observações soltas.
4. **Manejável** — agentes menores conseguem auditar, atualizar e retomar sem reconstruir a conversa.

A arquitetura alvo usa:

```text
SOUL → regras de comportamento
MEMORY/USER → bootstrap mínimo
Hindsight → recall semântico operacional
Acervo → fonte canônica estruturada
session_search → literalidade histórica
skills → procedimentos reutilizáveis
```

## Definição de pronto global

- [ ] `SOUL.md` contém regra explícita de recuperação via Hindsight.
- [ ] Hindsight opera como memória semântica sob demanda.
- [ ] `MEMORY.md` cai para 35%–50% de uso.
- [ ] AcervoIndex permite localizar arquivos canônicos via Hindsight.
- [ ] Write hook indexa novas escritas canônicas.
- [ ] Rotina diária reconcilia drift por hash.
- [ ] Agentes menores registram progresso em `context/memory-excellence-progress.md` e handoffs em `context/memory-excellence-handoff-log.md`.
- [ ] Smoke tests provam recall, leitura do Acervo e economia de token.

## Ordem de execução

### Fase 0 — Baseline e contrato

**Objetivo:** congelar estado inicial e garantir que todos os agentes usem a mesma regra.

Tarefas:

1. Ler ADR-019, ADR-020, ADR-021 e `contracts/memory-routing-contract.md`.
2. Capturar baseline:
   - tamanho de `MEMORY.md` e `USER.md`;
   - `hermes memory status`;
   - `~/.hermes/hindsight/config.json` sem segredos;
   - quantidade aproximada de arquivos indexáveis no Acervo.
3. Registrar baseline no progress file.

Aceite:

- [ ] Baseline escrito no progress file.
- [ ] Nenhuma mudança de configuração feita nesta fase.

### Fase 1 — SOUL e comportamento de recuperação

**Objetivo:** fazer o agente usar Hindsight antes de responder sobre contexto passado.

Tarefas:

1. Preparar patch no `~/.hermes/SOUL.md` fora do bloco `COMPILED_RULES`.
2. Inserir regra curta:
   - Hindsight primeiro para passado, estado, decisões, contexto multi-sessão;
   - Acervo decide quando houver fonte canônica;
   - session_search para literalidade.
3. Reiniciar sessão/gateway quando necessário.
4. Testar com pergunta sobre decisão passada.

Aceite:

- [ ] SOUL contém a regra.
- [ ] Novo turno chama `hindsight_recall` antes de responder a uma pergunta contextual.
- [ ] Teste registrado no handoff log.

### Fase 2 — Hindsight tools-first

**Objetivo:** reduzir contexto automático e forçar recuperação explícita.

Tarefas:

1. Atualizar `~/.hermes/hindsight/config.json`:
   - `memory_mode: tools`;
   - `auto_recall: false`;
   - manter `auto_retain: true`;
   - manter `recall_budget: low`;
   - manter `recall_types: observation`.
2. Reiniciar gateway ou abrir nova sessão.
3. Rodar smoke:
   - `hindsight_retain` com marcador controlado;
   - `hindsight_recall` do marcador;
   - `hindsight_reflect` sobre tema conhecido.

Aceite:

- [ ] Config validada em disco.
- [ ] Provider continua `available`.
- [ ] Tools Hindsight funcionam em nova sessão.

### Fase 3 — Consolidação da memória rápida

**Objetivo:** remover excesso de `MEMORY.md` e migrar conteúdo para Hindsight/Acervo.

Tarefas:

1. Classificar cada entrada atual de `MEMORY.md`:
   - manter;
   - migrar para Hindsight;
   - migrar para Acervo;
   - remover por obsolescência.
2. Criar DRAFT de substituição antes de aplicar.
3. Aplicar mudanças via ferramenta `memory` em batch.
4. Reter no Hindsight os fatos operacionais removidos.
5. Promover decisões/conhecimento ao Acervo quando necessário.

Aceite:

- [ ] `MEMORY.md` abaixo de 50%.
- [ ] Entradas removidas têm destino explícito.
- [ ] Nenhum segredo foi copiado para Hindsight ou Acervo.

### Fase 4 — AcervoIndex mínimo funcional

**Objetivo:** criar script que indexa arquivos canônicos do Acervo no Hindsight.

Tarefas:

1. Implementar `acervo/global/tools/acervo_hindsight_index.py` conforme `tools/acervo-hindsight-indexer-spec.md`.
2. Criar manifesto local em `acervo/global/tools/state/acervo_hindsight_index.json`.
3. Rodar `scan --microverso exocortex-dev`.
4. Validar que `hindsight_recall` retorna caminhos do Acervo.

Aceite:

- [ ] Script roda sem erro.
- [ ] Hash evita reindexação desnecessária.
- [ ] `deprecated`, `_archive`, `.quarantine` e `raw` são ignorados.
- [ ] Recall retorna `path` e resumo.

### Fase 5 — Write hook

**Objetivo:** indexar novas escritas canônicas no fluxo normal.

Tarefas:

1. Integrar chamada `index-file` após writes do `excrtx-memory-manager` ou wrapper equivalente.
2. Garantir que hook só roda depois de:
   - validação de frontmatter;
   - semantic revision;
   - log/index do microverso.
3. Criar teste com novo arquivo pequeno em `knowledge/`.

Aceite:

- [ ] Novo arquivo canônico aparece no Hindsight sem rotina diária.
- [ ] Falha no Hindsight não cancela escrita canônica; apenas registra erro.
- [ ] Erro entra no progress/log.

### Fase 6 — Rotina diária de reconciliação

**Objetivo:** corrigir drift e criar observabilidade.

Tarefas:

1. Criar cron diário com prompt self-contained.
2. Rodar `scan --all`.
3. Entregar relatório ao executivo com:
   - novos indexados;
   - alterados;
   - órfãos;
   - ignorados por lifecycle;
   - erros.
4. Não apagar entradas Hindsight na primeira versão; apenas reportar órfãos.

Aceite:

- [ ] Cron criado e executável sob demanda.
- [ ] Relatório compacto entregue no home channel.
- [ ] Nenhum arquivo em `raw`, `_archive`, `.quarantine` foi indexado.

### Fase 7 — Avaliação e hardening

**Objetivo:** provar que o sistema ficou melhor.

Métricas:

| Métrica | Alvo |
|---|---:|
| `MEMORY.md` usage | 35%–50% |
| Perguntas contextuais com Hindsight | ≥ 90% em amostra manual |
| Respostas sobre decisões com Acervo lido | ≥ 90% |
| Recall irrelevante do Hindsight | < 20% |
| Erros de indexação diária | 0 críticos |

Tarefas:

1. Rodar bateria de 10 prompts de memória.
2. Registrar resultados no progress file.
3. Ajustar SOUL/skill/config se o agente falhar.

Aceite:

- [ ] Métricas registradas.
- [ ] Falhas viraram issues locais ou GitHub, se necessário.
- [ ] Plano marcado como concluído.

## Pacotes para agentes menores

### Agente A — Baseline e SOUL

Referências obrigatórias:

- `decisions/adr-019-memory-operating-model.md`
- `contracts/memory-routing-contract.md`
- `context/memory-excellence-progress.md`

Saída esperada:

- baseline preenchido;
- DRAFT de patch do SOUL;
- smoke inicial registrado.

### Agente B — Consolidação da memória rápida

Referências obrigatórias:

- `decisions/adr-021-memory-fast-layer-budget.md`
- `context/memory-excellence-progress.md`

Saída esperada:

- tabela de migração de entradas;
- `MEMORY.md` reduzido;
- retenções Hindsight feitas;
- registro de destino por entrada.

### Agente C — Indexador AcervoIndex

Referências obrigatórias:

- `decisions/adr-020-acervo-hindsight-index.md`
- `tools/acervo-hindsight-indexer-spec.md`

Saída esperada:

- script implementado;
- manifesto local;
- teste `scan --microverso exocortex-dev`;
- recall com caminho do Acervo.

### Agente D — Hook e cron

Referências obrigatórias:

- `tools/acervo-hindsight-indexer-spec.md`
- `context/memory-excellence-handoff-log.md`

Saída esperada:

- write hook integrado;
- cron diário criado;
- relatório de reconciliação validado.

### Agente E — Avaliação

Referências obrigatórias:

- todos os ADRs;
- progress file;
- handoff log.

Saída esperada:

- bateria de 10 prompts;
- métricas finais;
- recomendações de ajuste.

## Protocolo de handoff

Ao terminar uma tarefa, o agente deve atualizar `context/memory-excellence-handoff-log.md` com:

```markdown
## YYYY-MM-DDTHH:MM:SSZ — Agente X — tarefa

- Estado: done|blocked|partial
- Arquivos alterados:
- Comandos/validações executadas:
- Decisões tomadas:
- Pendências:
- Próximo agente recomendado:
```

Sem esse handoff, a tarefa não é considerada concluída.

> Canonicalizado em `micro/exocortex-ops/workflows/memory-excellence-execution-plan.md` a partir de `micro/exocortex-dev/workflows/memory-excellence-execution-plan.md` em 2026-06-21T21:50:00Z.

