---
title: Hermes deve rodar dentro de ~/exocortex em produção
created: 2026-05-31
updated: 2026-05-31
nature: conhecimento
kind: decision
scope_mode: micro
scope_slug: hermes-setup
applies_to: [global]
authority: canonical
operational_mode: blocking
stability: active
sources: [conversation:2026-05-31]
derived_from: [exocortex-home-layout-discussion]
confidence: high
promotion_policy: candidate-global
upstream:
  source_skill: autonomous-ai-agents/hermes-agent
  assumed_version: null
  coupling: adapter-only
tags: [architecture, hermes, cwd, exocortex-home, acervo]
---

# Decisão — Hermes deve rodar dentro de ~/exocortex em produção

## Decisão

Para novos Hermes Exocórtex, o processo Hermes deve operar com diretório de trabalho em:

```text
~/exocortex
```

O runtime Hermes permanece separado:

```text
HERMES_HOME=~/.hermes
```

A raiz operacional do Exocórtex passa a ser:

```text
EXOCORTEX_HOME=~/exocortex
```

O Acervo Cognitivo canônico passa a ser:

```text
ACERVO=~/exocortex/acervo
```

`~/.hermes/acervo` pode existir apenas como symlink de compatibilidade para `~/exocortex/acervo`. Não é a fonte conceitual canônica em novas instalações.

## Racional

`~/.hermes` é control plane: config, credenciais, auth, sessões, logs, skills, profiles e estado interno do Hermes.

`~/exocortex` é workspace cognitivo: Acervo, microversos, inbox, artifacts, contratos, workflows e artefatos operacionais do Exocórtex.

Rodar Hermes dentro de `~/exocortex` melhora o comportamento default do agente porque paths relativos, buscas e arquivos auxiliares passam a nascer no cockpit cognitivo, não dentro do runtime sensível.

## Contrato operacional

- CLI: iniciar com `cd ~/exocortex && hermes`.
- Gateway/produção: configurar `terminal.cwd` para o path absoluto de `~/exocortex`.
- Setup: criar `~/exocortex` antes de validar o Acervo.
- Setup: resolver `ACERVO` a partir de `EXOCORTEX_HOME`, não de `HERMES_HOME`.
- Compatibilidade: manter `~/.hermes/acervo -> ~/exocortex/acervo` quando necessário.
- Skills: scripts devem aceitar `ACERVO` explícito e usar `EXOCORTEX_HOME` como fallback.

## Anti-decisões

- Não rodar produção dentro de `~/.hermes`.
- Não transformar `HERMES_HOME` em workspace do Exocórtex.
- Não misturar credenciais, sessões e logs do Hermes com o Acervo.
- Não mover skills Hermes para `~/exocortex`; elas continuam em `~/.hermes/skills`.

## Implicação para refatoração

A refatoração para novos Hermes deve atualizar setup, skills, scripts e workflows para a separação:

```text
~/.hermes      = runtime Hermes
~/exocortex    = workspace Exocórtex
~/exocortex/acervo = Acervo canônico
```

Qualquer referência operacional nova a `~/.hermes/acervo` deve ser tratada como legado ou compatibilidade.
