---
title: "LotoState by ALEQIA — Workflow Specs → Tasks"
type: knowledge
description: "Fluxo de derivação de specs em tarefas de implementação para o LotoState"
class: volátil
timestamp: "2026-07-05"
created_at: "2026-07-05T19:56:31Z"
created: "2026-07-05"
updated: "2026-07-06"
nature: workflows
excrtx_type: workflow
tags: [projeto-d, lotostate, aleqia, workflow, agentic, specs, tasks]
confidence: high
sources:
  - /home/elder/.hermes/cache/documents/doc_c15191a2021b_PRD_LotoState_by_ALEQIA.md
---

# LotoState by ALEQIA — Workflow Specs → Tasks

Fluxo recomendado pelo PRD para transformar especificação em implementação revisável por agentes.

## Trigger

Usar este workflow quando o Projeto D precisar transformar visão de produto do LotoState em backlog executável, contratos técnicos ou iteração de build.

## Artefatos-fonte esperados

1. `PRD.md`
2. `DOMAIN.md`
3. `UX_SPEC.md`
4. `API_SPEC.md`
5. `DATA_SPEC.md`
6. `SECURITY_PRIVACY.md`
7. `TEST_PLAN.md`
8. `TASKS.md`
9. `AGENTS.md`
10. `CHANGELOG.md`

## Sequência operacional

### Etapa 1 — consolidar a verdade de produto
- validar que o PRD identifica requisitos, prioridades, personas, regras de negócio, critérios de aceite e dependências
- separar proposta aprovada de recomendação ainda aberta
- preservar perguntas em aberto como backlog de decisão, não como implementação implícita

### Etapa 2 — extrair contratos técnicos
- derivar entidades, invariantes e fronteiras de serviço
- derivar payloads e envelopes de erro
- derivar NFRs e critérios de segurança
- explicitar onde o backend é autoridade e onde o frontend apenas apresenta estado público

### Etapa 3 — quebrar em épicos
Épicos MVP preservados do PRD:
- base de repositório independente, auth e design system
- domínio e banco
- dados de loteria e concursos
- integração do motor ALEQIA D
- monitor mobile MVP
- jogos e conferidor
- carteira
- planos, checkout e entitlement
- web MVP
- notificações/WhatsApp
- testes, observabilidade e release

### Etapa 4 — derivar tasks agenticas
Cada task deve:
- mapear requisito-fonte por ID
- manter escopo coeso
- alterar preferencialmente até 5 arquivos centrais
- declarar comando de teste
- ter rollback mental claro
- produzir diff revisável

### Etapa 5 — validar pronto para execução
Definition of Ready mínima:
- requisito-fonte identificado
- aceite objetivo
- escopo de arquivos provável
- comando de teste definido
- fixture ou dado de exemplo quando necessário
- risco especial nomeado

### Etapa 6 — validar pronto para merge
Definition of Done mínima:
- código implementado
- testes passando
- lint/typecheck passando
- nenhum dado sensível em log
- nenhuma exposição de fórmula interna
- documentação atualizada se contrato mudou
- analytics implementado quando aplicável
- revisão humana aprovada

## Guardrails para execução agentica

1. nunca expor fórmulas ALEQIA D em superfície pública
2. nunca hardcodar plano do usuário no cliente
3. nunca tratar geração de jogo como envio oficial à Caixa
4. nunca ignorar bloqueios por plano
5. sempre criar testes para entitlement, jogo e carteira
6. sempre manter rastreabilidade entre requisito, código e teste

## Saída esperada

Ao final do workflow, o projeto deve ter:
- backlog derivado do PRD em tasks pequenas e testáveis
- contratos técnicos estáveis para backend e frontend
- critérios de revisão claros para agentes e humanos
