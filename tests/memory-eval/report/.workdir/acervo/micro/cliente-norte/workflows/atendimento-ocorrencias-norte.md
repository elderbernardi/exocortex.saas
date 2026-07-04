---
schema: acervo/v0.2
type: workflow
title: "Atendimento de ocorrências da conta Norte"
description: "Fluxo de resposta a incidente: aviso em 1h, plano em 48h, follow-up formal com Ricardo por e-mail"
tags: [sop, ocorrencia]
created_at: 2026-03-10T10:00:00Z
class: perene
status: active
epistemic: rule
confidence: high
sources: [{type: executive, ref: "session://tg-2026-03-08#turn-3"}]
observed_at: 2026-03-08
extraction: agent
entities: [norte-mineracao]
---
1. Incidente detectado → avisar Ana Beltrão em até 1h (telefone + e-mail).
2. Plano de ação formal em até 48h, assinado por Marina.
3. Follow-up com Ricardo por e-mail com resumo executivo.
4. Registrar o evento no histórico de atrasos da conta.
