---
schema: acervo/v0.2
type: context
title: Exocórtex Dev
description: Desenvolvimento do framework Exocórtex.IA — skills, harness, acervo, integrações e evolução do sistema com Hermes Agent.
tags: []
timestamp: 2026-06-08
class: perene
status: active
epistemic: fact
created_at: 2026-06-08T00:00:00Z
last_accessed_at: 2026-06-08T00:00:00Z
domain: Desenvolvimento do Exocórtex
excrtx_type: project
slug: exocortex-dev
updated: 2026-06-11
priority: high
created: 2026-06-08
nature: _meta
---

# Exocórtex Dev

Microverso para o desenvolvimento do próprio Exocórtex.IA. Cobre design e implementação de skills, harness, estrutura do acervo, integrações, qualidade e evolução do framework.

## Estado

- Status: active
- Onboarding: completo (documentação e base de conhecimento estruturadas)
- Relação com exocortex-ops: este microverso é para desenvolvimento do produto; exocortex-ops é para operação e manutenção da instância ativa.

## Arquivos Catalogados

### Meta / Convenções
- `_meta/SCHEMA.md` — especificação e convenções de tags/natures deste wiki.
- `_meta/index.md` — este arquivo (catálogo de páginas).
- `_meta/log.md` — log append-only de alterações no microverso.

### Context (Cenário Ativo)
- [current-state.md](file:///home/elder/projetos/projetob/exocortex.saas/acervo/micro/exocortex-dev/context/current-state.md) — roadmap ativo e marcos de desenvolvimento.

### Contracts (Políticas e Padrões)
- [development-standards.md](file:///home/elder/projetos/projetob/exocortex.saas/acervo/micro/exocortex-dev/contracts/development-standards.md) — padrões de código (Python/Node) e requisitos de skills.

### Decisions (Decisões de Design)
- [skill-vs-mcp-selection.md](file:///home/elder/projetos/projetob/exocortex.saas/acervo/micro/exocortex-dev/decisions/skill-vs-mcp-selection.md) — ADR-006: critérios de decisão entre criar uma Skill ou usar um servidor MCP.
- [adr-022-acervo-mcp-control-plane.md](file:///home/elder/projetos/projetob/exocortex.saas/acervo/micro/exocortex-dev/decisions/adr-022-acervo-mcp-control-plane.md) — ADR-022: filesystem como verdade física; core semântico local como verdade operacional; CLI/MCP como superfícies do Acervo.

### Knowledge (Arquitetura e Conceitos)
- [architecture.md](file:///home/elder/projetos/projetob/exocortex.saas/acervo/micro/exocortex-dev/knowledge/architecture.md) — arquitetura geral e fluxo de execução (Trilho A vs. Trilho B).

### Workflows (SOPs e Processos)
- [create-custom-skill.md](file:///home/elder/projetos/projetob/exocortex.saas/acervo/micro/exocortex-dev/workflows/create-custom-skill.md) — guia passo a passo para criar e registrar uma nova skill customizada.
- [run-preflight-checks.md](file:///home/elder/projetos/projetob/exocortex.saas/acervo/micro/exocortex-dev/workflows/run-preflight-checks.md) — SOP para rodar validações pré-commit (`checklist.py`/`verify_all.py`).

## Próxima ação

Calibrar novas skills e expandir a suite de testes conforme novos requisitos surgirem.

### Knowledge
- `micro/exocortex-dev/knowledge/purpose-docbrain-smoke.md`
