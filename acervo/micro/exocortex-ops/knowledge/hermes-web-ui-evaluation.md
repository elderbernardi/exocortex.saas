---
type: knowledge
title: '[SUPERSEDED] Avaliação do hermes-web-ui (EKKOLearnAI) — descartado por licença BSL 1.1'
description: '**Status**: SUPERSEDED em 2026-06-15.'
tags: [hermes-web-ui, dashboard, provisioning, saas, operator-surface, bsl-license, superseded]
timestamp: 2026-06-12
class: volátil
created_at: 2026-06-12T00:00:00Z
last_accessed_at: 2026-06-12T00:00:00Z
updated: 2026-06-15
nature: knowledge
kind: assessment
scope_slug: exocortex-ops
authority: observed
stability: superseded
lifecycle_state: archived
sources: ['repo:/home/elder/work/repo-assessments/hermes-web-ui']
confidence: high
created: 2026-06-12
---

# [SUPERSEDED] Avaliação do hermes-web-ui (EKKOLearnAI)

> **Status**: SUPERSEDED em 2026-06-15.
>
> O componente `EKKOLearnAI/hermes-web-ui` (redirecionado para `EKKOLearnAI/hermes-studio`) foi
> removido do codebase por incompatibilidade de licença. A licença detectada é **BSL 1.1**
> (Business Source License) com `Change Date: 2029-05-10`, que **não permite derivações comerciais**
> até essa data.
>
> **Substituto avaliado**: `nesquena/hermes-webui` (licença MIT — uso comercial irrestrito).
> A integração do substituto será feita em fase separada.

---

## Veredito original (agora invalidado)

`hermes-web-ui` (EKKOLearnAI) servia bem como cockpit operacional do Hermes, mas foi descartado
por risco jurídico da licença BSL 1.1.

## Motivo da remoção

- Licença BSL 1.1 detectada no LICENSE remoto do upstream.
- `commercial_use_requires_license: true` — incompatível com uso SaaS comercial do Exocórtex.
- Remoção completa de todos os artefatos, scripts, testes e referências em 2026-06-15.

## Referências removidas

- `provision/hermes-web-ui/` (diretório completo removido)
- `setup/step-10b-hermes-web-ui.sh` (removido)
- `tests/test_provision_env_bindings.py` (removido)
- `docs/plans/hermes-web-ui-barebone-source-controlled-2026-06-14.md` (removido)
- `docs/plans/hermes-web-ui-private-ops-hardening-2026-06-14.md` (removido)
- `docs/research/hermes-web-ui-provisioning-plan-2026-06-12.md` (removido)
- Entrada `hermes-web-ui` em `provision/sources/sources.lock.yaml` (removida)
