---
schema: acervo/v0.2
type: contract
title: Política de verificação do runtime
description: 'Estado operacional exige ferramenta. Não responder de memória sobre:'
tags: [runtime, verificacao, ferramentas]
timestamp: 2026-06-05
class: perene
status: active
created_at: 2026-06-05T00:00:00Z
last_accessed_at: 2026-06-05T00:00:00Z
updated: 2026-06-05
nature: contracts
kind: rule
scope_slug: exocortex-ops
authority: canonical
stability: active
lifecycle_state: active
created: 2026-06-05
---

# Política de verificação do runtime

## Regra

Estado operacional exige ferramenta. Não responder de memória sobre:

- versão do Hermes;
- profile ativo;
- modelo configurado;
- MCPs;
- providers de memória;
- paths reais;
- git status;
- data/hora;
- processos, portas ou disco.

## Evidência

Relatórios operacionais devem citar comando, arquivo lido ou tool usada.

## Falha

Se o comando falhar, marcar o componente como `unknown` ou `degraded`. Não preencher lacunas com suposição.
