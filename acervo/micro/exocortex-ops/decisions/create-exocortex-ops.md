---
title: Criar Microverso Exocortex Ops
created: 2026-06-05
updated: 2026-06-05
nature: decisions
tags: [microverso, ops, setup, canonical]
sources: [conversation:user-request]
confidence: high
---

# Decisão: criar Exocortex Ops

## Contexto

O acervo possuía estrutura macro/global/shared e o microverso `estudio-criativo`, mas não havia um domínio próprio para setup e operação do Exocórtex.

## Decisão

Criar `exocortex-ops` como microverso canônico de setup, operação, manutenção, diagnóstico e evolução do Exocórtex.IA sobre Hermes Agent.

## Escopo

Inclui:

- runtime Hermes;
- perfil ativo e isolamento entre profiles;
- toolsets e MCPs;
- providers de memória;
- DocBrain, NotebookLM e integrações operacionais;
- self-checks e auditorias de drift;
- decisões sobre setup replicável;
- governança Draft-First para mudanças sensíveis.

Exclui:

- identidade pessoal do executivo;
- conteúdo de clientes/projetos;
- produção criativa;
- segredos e credenciais.

## Justificativa

Operações do próprio Exocórtex precisam de memória isolada. Sem esse microverso, decisões técnicas ficam espalhadas entre skills, conversa, global e memória operacional.

## Status

Aprovado por pedido explícito do executivo.
