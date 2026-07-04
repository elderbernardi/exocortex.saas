---
schema: acervo/v0.2
type: knowledge
title: Localização do runbook de instalação (INSTALL.md)
description: Onde encontrar o INSTALL.md — ele vive no repositório-fonte exocortex.saas e não é copiado para o runtime.
tags: [install, runbook, agents, source-repo]
timestamp: 2026-06-22
class: volátil
status: active
epistemic: fact
created_at: 2026-06-22T00:00:00Z
last_accessed_at: 2026-06-22T00:00:00Z
updated: 2026-06-22
nature: knowledge
kind: registry
scope_slug: exocortex-ops
authority: canonical
stability: active
lifecycle_state: active
created: 2026-06-22
---

# Localização do runbook de instalação (INSTALL.md)

O `INSTALL.md` — runbook estruturado de instalação para agentes de IA — **não é
copiado para o runtime**. O `setup.sh` provisiona apenas skills, profiles, bundles
e o Acervo para `$HERMES_HOME` / `$EXOCORTEX_HOME`; o `INSTALL.md` permanece no
**repositório-fonte**.

## Onde encontrar

- **Repositório-fonte canônico:** `elderbernardi/exocortex.saas`
  (`https://github.com/elderbernardi/exocortex.saas.git`), arquivo `INSTALL.md` na raiz.
- **Checkout local usado para provisionar este runtime:** o clone de onde o
  `setup.sh` foi executado (não há cópia em `~/.hermes` nem em `~/exocortex`).

## Como um agente deve proceder

1. Se já estiver dentro do checkout do repo, o caminho é `./INSTALL.md`.
2. Caso contrário, clonar a fonte e consultar lá:
   `git clone https://github.com/elderbernardi/exocortex.saas.git && cd exocortex.saas`
   e abrir `INSTALL.md`.
3. Documentos correlatos no mesmo repo: `README.md`, `HARNESS.md`, `CHANGELOG.md`.

> Nota: por decisão de design, o runbook **não** é duplicado no runtime — esta
> página é o ponteiro canônico. Se a política mudar, atualize aqui e no `README.md`.
