---
title: Contrato — Hindsight como Memória Operacional Auxiliar
created: 2026-05-31
updated: 2026-06-01
nature: instrucoes
kind: contract
scope_mode: micro
scope_slug: hermes-setup
applies_to: [global]
authority: canonical
operational_mode: blocking
stability: active
sources: [plugins/memory/hindsight/README.md, autonomous-ai-agents/hermes-agent]
derived_from: []
confidence: high
promotion_policy: candidate-global
upstream:
  source_skill: autonomous-ai-agents/hermes-agent
  assumed_version: null
  coupling: adapter-only
tags: [hindsight, memory, exocortex, operational-memory, setup]
---

# Contrato — Hindsight como Memória Operacional Auxiliar

## Decisão

Hindsight pode ser usado pelo Exocórtex.IA como camada auxiliar de memória operacional semântica. Ele observa, retém, recupera e sintetiza contexto útil para continuidade entre sessões.

Hindsight não é fonte canônica do Exocórtex. O Acervo Cognitivo v2 permanece como patrimônio cognitivo auditável. SOUL, contratos do Acervo e skills carregadas têm precedência sobre qualquer memória recuperada.

## Precedência

Em caso de conflito, aplicar esta ordem:

1. SOUL e instruções de sistema vigentes.
2. Contratos do Acervo com `operational_mode: blocking`.
3. Skills carregadas e workflows canônicos.
4. Hindsight como memória operacional ativa.
5. Built-in memory apenas quando Hindsight estiver desativado.
6. Acervo Cognitivo v2 para conhecimento, decisões e processos canônicos.
7. Session Search para histórico literal.

Se Hindsight contradizer camada superior, Hindsight perde.

## Papel permitido

Hindsight pode:

- recuperar padrões operacionais recorrentes;
- sugerir contexto útil para a conversa atual;
- consolidar observações semânticas de interações;
- reduzir perguntas repetidas;
- apoiar identificação de conteúdo candidato ao Acervo;
- apoiar continuidade entre perfis, plataformas e sessões.

## Papel proibido

Hindsight não pode:

- substituir o Acervo;
- declarar decisões canônicas;
- alterar contratos, workflows ou skills;
- enviar dados para fora sem aprovação quando a ação for externa;
- rebaixar exigências de Draft-First;
- tratar observações recuperadas como verdade final;
- promover automaticamente informação para `memory`, skill ou Acervo.

## Política de retenção

Reter apenas informação que melhora operação futura:

- preferências estáveis;
- padrões recorrentes de decisão;
- restrições operacionais;
- relações entre projetos, microversos e workflows;
- correções explícitas feitas pelo executivo;
- lições operacionais reutilizáveis;
- decisões candidatas ainda não canonizadas.

Evitar reter:

- cumprimentos e mensagens triviais;
- IDs, URLs e estados efêmeros;
- rascunhos não aprovados;
- segredos e credenciais;
- dados pessoais sem necessidade operacional;
- resultados transitórios de tarefas.

## Política de recall

A configuração inicial deve privilegiar baixo ruído:

- `recall_types: observation`;
- `recall_budget: low`;
- `recall_max_tokens` entre 1000 e 1200;
- `retain_every_n_turns: 2`;
- `memory_mode: hybrid`;
- `reflect` sob demanda, não como camada dominante.

## Promoção para o Acervo

Memória recuperada pelo Hindsight deve ser tratada como observação.

Fluxo de promoção:

```text
observação Hindsight
→ validação contra contexto atual
→ candidato explícito
→ Acervo/decisions, Acervo/contracts, Acervo/workflows, skill ou built-in memory
```

Só decisões explícitas do executivo ou contratos aceitos podem virar `authority: canonical`.

## Reversibilidade

A adoção deve ser reversível. O Exocórtex deve continuar funcional com:

```bash
hermes config set memory.provider none
```

ou com retorno ao provider built-in only, mantendo built-in memory, Session Search, skills e Acervo.

## Operação local padronizada

- Hindsight local deve rodar em diretório dedicado `~/.hermes/hindsight-local`.
- Persistência deve usar volume local em `~/.hermes/hindsight-local/data`.
- Exclusão de memória em update exige confirmação explícita por parâmetro.

## Política de escopo de memória

- Um Hindsight por instância Hermes.
- Neste setup, perfis `exec` e `evol` compartilham o mesmo bank (`bank_id_template: exocortex`).
- Não tratar perfis como tenants isolados.
