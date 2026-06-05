---
title: Template — snapshot funcional
created: 2026-06-05
updated: 2026-06-05
nature: templates
kind: template
scope_slug: exocortex-ops
authority: canonical
stability: active
lifecycle_state: active
tags: [snapshot, template, runtime]
---

# Template — snapshot funcional

```md
---
title: Snapshot funcional — {motivo}
created: YYYY-MM-DD
updated: YYYY-MM-DD
nature: context
kind: snapshot
scope_slug: exocortex-ops
authority: observed
stability: active
lifecycle_state: observed
snapshot_phase: before|after
snapshot_reason: setup|provider-change|profile-change|drift-audit|incident
confidence: high|medium|low
tags: [snapshot, ops]
---

# Snapshot funcional — {motivo}

## Escopo
- Motivo:
- Data/hora:
- Profile Hermes ativo:
- HERMES_HOME:
- Acervo canônico:

## Estado observado
- Hermes:
- Profiles:
- MCPs:
- Memory:
- Skills críticas:
- Microversos:

## Drift
| Área | Esperado | Observado | Severidade | Próxima ação |
|---|---|---|---|---|

## Comandos executados
```bash
...
```
```
