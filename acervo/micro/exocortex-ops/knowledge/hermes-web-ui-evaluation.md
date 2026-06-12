---
title: Avaliação do hermes-web-ui como base operacional do Exocórtex SaaS
created: 2026-06-12
updated: 2026-06-12
nature: knowledge
kind: assessment
scope_slug: exocortex-ops
authority: observed
stability: draft
lifecycle_state: observed
tags: [hermes-web-ui, dashboard, provisioning, saas, operator-surface]
sources:
  - repo:/home/elder/work/repo-assessments/hermes-web-ui
  - doc:docs/research/hermes-web-ui-provisioning-plan-2026-06-12.md
confidence: high
---

# Avaliação do hermes-web-ui como base operacional do Exocórtex SaaS

## Veredito

`hermes-web-ui` serve bem como cockpit operacional do Hermes, mas não deve virar superfície pública do Exocórtex SaaS sem hardening explícito.

## O que foi validado

- `npm ci --ignore-scripts` concluiu com sucesso.
- `npm run test` concluiu com sucesso.
- `npm run build` concluiu com sucesso.
- O servidor compilado respondeu em `/health` durante smoke real em porta isolada.
- Há cobertura explícita para write approvals, session sync, profiles, jobs, terminal, files e bridge com Hermes CLI.

## Riscos observados

- Bootstrap administrativo inseguro e presença de defaults sensíveis no backend.
- `npm audit --json` retornou vulnerabilidades abertas.
- Forte acoplamento do backend com subprocessos da CLI Hermes.
- Pacote desktop com runtime empacotado e sinais de auto-update, o que não é a trilha recomendada para o setup inicial do Exocórtex.
- Superfície HTTP ampla demais para exposição pública direta sem camada de segurança, isolamento e política multi-tenant.

## Coalizão recomendada

### O que a UI faz bem

- Operação do runtime Hermes.
- Sessões, logs, jobs, profiles, MCPs, arquivos e terminal.
- Aprovações pendentes de escrita.
- Supervisão do estado do agente e do gateway.

### O que continua sendo do Exocórtex

- Identidade operacional.
- Vetorização execução/evolução/manutenção.
- Draft-First.
- Macroverso, microversos e acervo.
- Governança semântica, memória e promoção de conhecimento.

## Implicação arquitetural

A recomendação é manter a separação de superfícies:

- **Executivo:** Telegram como interface primária.
- **Operador:** `hermes-web-ui` como cockpit privado.
- **Administrador:** CLI/TUI Hermes para manutenção e recuperação.

## Trilha recomendada

1. Fork controlado e CI reprodutível.
2. Hardening obrigatório antes de qualquer exposição remota.
3. Empacotamento container-first.
4. Integração progressiva com o setup do `exocortex.saas`.

## Artefato detalhado

Plano completo migrado para:

- `docs/research/hermes-web-ui-provisioning-plan-2026-06-12.md`
