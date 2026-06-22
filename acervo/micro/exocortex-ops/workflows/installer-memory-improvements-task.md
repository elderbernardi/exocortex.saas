---
type: knowledge
title: Tarefa — Consolidar instalador da memória Exocórtex/Hermes
description: Tarefa para provisionar, configurar, testar e operacionalizar a reforma
  de memória no instalador.
tags:
- memory
- installer
- setup
- hindsight
- acervo
- smoke-test
timestamp: '2026-06-21'
class: volátil
created_at: '2026-06-21T21:13:33Z'
nature: workflows
excrtx_type: workflow
confidence: high
canonical_from: micro/exocortex-dev/workflows/installer-memory-improvements-task.md
promoted_at: '2026-06-21T21:50:00Z'
scope_slug: exocortex-ops
absorbed_from: micro/exocortex-dev/workflows/installer-memory-improvements-task.md
---

# Tarefa — Consolidar instalador da memória Exocórtex/Hermes

## Objetivo

Consolidar o instalador/provisionador do Exocórtex/Hermes para reproduzir, em instalação limpa ou atualização, as decisões e ações desta sessão de melhoramento da memória.

## Escopo obrigatório

O instalador deve:

1. **Provisionar Hindsight**
   - garantir provider `hindsight` ativo;
   - preservar built-in memory;
   - manter banco `exocortex` ou bank configurado;
   - não sobrescrever credenciais existentes.

2. **Configurar modo tools-first**
   - `memory_mode: tools`;
   - `auto_recall: false`;
   - `auto_retain: true`;
   - `recall_budget: low`;
   - `recall_max_input_chars: 800`.

3. **Aplicar protocolo no SOUL**
   - inserir ou atualizar bloco `Protocolo de Memória e Contexto` fora de `COMPILED_RULES`;
   - idempotente: rodar duas vezes não duplica o bloco;
   - regra curta preservada: Hindsight recupera; Acervo confirma; `session_search` prova; memória rápida só inicializa.

4. **Consolidar memória rápida**
   - manter `MEMORY.md` apenas com invariantes de bootstrap;
   - não copiar segredos para Hindsight ou Acervo;
   - preservar `USER.md` para preferências duráveis do executivo;
   - migrar fatos operacionais para Hindsight quando seguro.

5. **Instalar AcervoIndex**
   - instalar `acervo/global/tools/acervo_hindsight_index.py`;
   - criar `acervo/global/tools/state/acervo_hindsight_index.json` quando ausente;
   - rodar `scan --microverso exocortex-dev` ou `scan --all` conforme perfil de instalação;
   - não indexar `raw/`, `_archive/`, `.quarantine/`, `state/`, `__pycache__` ou arquivos `deprecated: true`.

6. **Registrar estado no Acervo**
   - atualizar `context/memory-excellence-progress.md`;
   - atualizar `context/memory-excellence-handoff-log.md`;
   - atualizar logs/indexes relevantes.

## Smoke test obrigatório

O instalador deve encerrar com uma bateria mínima:

```bash
hermes memory status
python "$ACERVO/global/tools/acervo_hindsight_index.py" scan --microverso exocortex-dev
python "$ACERVO/global/tools/acervo_hindsight_index.py" report
hermes chat -q 'O que decidimos sobre o modelo operacional de memória do Exocórtex? Responda em até 5 linhas e cite a origem.' --provider openai-codex -m gpt-5.4 -v --toolsets memory,file,skills,session_search,terminal
```

Critérios:

- provider `hindsight` disponível;
- config em disco mostra `memory_mode: tools`, `auto_recall: false`, `auto_retain: true`;
- `MEMORY.md` abaixo de 50% do limite;
- AcervoIndex reporta entradas e zero erros;
- nova sessão chama `hindsight_recall` antes de responder pergunta contextual;
- resposta lê arquivo canônico do Acervo antes de concluir;
- se provider default falhar por credencial, smoke deve tentar provider alternativo configurado e registrar o bloqueio.

## Prompt de aprimoramento para agente executor

Use este prompt ao retomar a implementação:

```text
Você é o agente executor da tarefa "Consolidar instalador da memória Exocórtex/Hermes".

Objetivo: transformar a reforma de memória executada em 2026-06-21 em fluxo idempotente de instalação/provisionamento.

Referências obrigatórias:
- /home/elder/exocortex/acervo/global/decisions/adr-019-memory-operating-model.md
- /home/elder/exocortex/acervo/global/decisions/adr-020-acervo-hindsight-index.md
- /home/elder/exocortex/acervo/global/decisions/adr-021-memory-fast-layer-budget.md
- /home/elder/exocortex/acervo/global/contracts/memory-routing-contract.md
- /home/elder/exocortex/acervo/global/tools/acervo-hindsight-indexer-spec.md
- /home/elder/exocortex/acervo/micro/exocortex-ops/context/memory-excellence-progress.md
- /home/elder/exocortex/acervo/micro/exocortex-ops/context/memory-excellence-handoff-log.md
- /home/elder/exocortex/acervo/global/tools/acervo_hindsight_index.py

Faça:
1. localizar o instalador/provisionador canônico do Exocórtex/Hermes;
2. adicionar etapa idempotente para Hindsight tools-first;
3. adicionar etapa idempotente para patch do SOUL;
4. instalar/atualizar AcervoIndex;
5. consolidar memória rápida sem apagar preferências duráveis;
6. implementar smoke test automatizado;
7. rodar testes reais;
8. registrar resultado no Acervo.

Não faça:
- não sobrescreva credenciais;
- não copie segredos para Hindsight/Acervo;
- não crie fonte paralela de verdade fora do Acervo;
- não trate Hindsight como canônico;
- não publique push/deploy sem DRAFT e aprovação.

Saída esperada:
- patch do instalador;
- smoke test executável;
- logs de validação;
- atualização dos arquivos de progresso/handoff;
- relatório curto com comandos executados e resultados reais.
```

## Saída esperada

- Instalador idempotente.
- Smoke test automatizado.
- Documentação curta de rollback.
- Validação real em ambiente local.
- Card Kanban atualizado com status final.

> Canonicalizado em `micro/exocortex-ops/workflows/installer-memory-improvements-task.md` a partir de `micro/exocortex-dev/workflows/installer-memory-improvements-task.md` em 2026-06-21T21:50:00Z.

