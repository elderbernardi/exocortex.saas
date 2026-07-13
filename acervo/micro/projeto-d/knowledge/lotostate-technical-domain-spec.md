---
title: "LotoState by ALEQIA — Domínio Técnico"
type: knowledge
description: "Modelo de domínio, invariantes, APIs e arquitetura técnica derivados do PRD do LotoState"
class: volátil
timestamp: "2026-07-05"
created_at: "2026-07-05T19:56:31Z"
created: "2026-07-05"
updated: "2026-07-05"
nature: knowledge
excrtx_type: fact
tags: [projeto-d, lotostate, aleqia, dominio, api, dados, arquitetura, lotofacil]
confidence: high
sources:
  - /home/elder/.hermes/cache/documents/doc_c15191a2021b_PRD_LotoState_by_ALEQIA.md
---

# LotoState by ALEQIA — Domínio Técnico

Este arquivo consolida a parte técnica do PRD: modelo de domínio, invariantes, ingestão, interface do motor, APIs e arquitetura recomendada.

## Entidades centrais

- `User`
- `Lottery`
- `Draw`
- `DrawResult`
- `DozenState`
- `UserPlan`
- `Entitlement`
- `BetSlip`
- `BetGame`
- `BetNumber`
- `WhatsAppConsent`

## Invariantes do domínio

| ID | Regra |
|---|---|
| INV-001 | Jogo Lotofácil deve conter entre 15 e 20 dezenas distintas |
| INV-002 | Resultado oficial Lotofácil deve conter 15 dezenas distintas |
| INV-003 | Usuário gratuito não recebe payload com mais de 5 dezenas liberadas |
| INV-004 | Dezena bloqueada não possui número no payload de UI |
| INV-005 | Toda mensagem WhatsApp exige consentimento ativo |
| INV-006 | Toda análise ALEQIA D referencia `model_version` |
| INV-007 | Cálculo de Carteira deve ser reproduzível a partir de slips, games e results |
| INV-008 | Sistema registra fonte e timestamp de dados oficiais |
| INV-009 | CPF não pode ser armazenado em texto puro |
| INV-010 | Frontend não executa algoritmo proprietário sensível |

## Motor ALEQIA D — responsabilidades

- consumir base canônica validada
- calcular estados por dezena e concurso
- produzir scores e estados públicos
- versionar snapshots
- suportar backtesting sem vazamento futuro
- ocultar fórmulas, janelas e parâmetros em endpoints públicos

## Regra de backtest

Para avaliar o concurso `n`, o motor só pode usar histórico até `n-1`.

## Dados oficiais e ingestão

### Pipeline
1. fonte oficial
2. collector
3. raw snapshot
4. parser
5. validation
6. canonical DB
7. model engine
8. API
9. clientes mobile/web

### Jobs mínimos
- `sync_lottery_catalog`
- `sync_draw_schedule`
- `sync_draw_results`
- `compute_aleqia_states`
- `send_result_notifications`
- `expire_entitlements`

## API pública sugerida

### Auth
- `POST /api/v1/auth/signup`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/password-reset/request`
- `POST /api/v1/auth/password-reset/confirm`

### Loterias e concursos
- `GET /api/v1/lotteries`
- `GET /api/v1/lotteries/{lotteryId}`
- `GET /api/v1/lotteries/{lotteryId}/draws/next`
- `GET /api/v1/lotteries/{lotteryId}/draws/recent`
- `GET /api/v1/draws/{drawId}`

### Monitor
- `GET /api/v1/monitor/{lotteryId}`
- `GET /api/v1/monitor/{lotteryId}/filters`
- `GET /api/v1/monitor/{lotteryId}/dozens/{number}`
- `GET /api/v1/monitor/{lotteryId}/comparison`

### Jogos
- `POST /api/v1/games/suggestions`
- `POST /api/v1/bet-slips`
- `GET /api/v1/bet-slips`
- `GET /api/v1/bet-slips/{id}`
- `POST /api/v1/bet-slips/{id}/check`
- `POST /api/v1/games/validate`

### Carteira
- `GET /api/v1/wallet/summary`
- `GET /api/v1/wallet/history`
- `PATCH /api/v1/bet-slips/{id}`
- `DELETE /api/v1/bet-slips/{id}`

### Monetização e consentimentos
- `GET /api/v1/plans`
- `GET /api/v1/me/entitlements`
- `POST /api/v1/checkout/session`
- `POST /api/v1/webhooks/payment`
- `POST /api/v1/entitlements/redeem`
- `GET /api/v1/me/consents`
- `POST /api/v1/me/consents/whatsapp`
- `DELETE /api/v1/me/consents/whatsapp`

## Arquitetura recomendada no PRD

| Camada | Recomendação |
|---|---|
| Mobile | React Native + Expo ou Flutter |
| Web | Next.js / React |
| Backend API | Python FastAPI |
| Model Engine | pacote Python interno |
| Banco | PostgreSQL |
| Cache | Redis |
| Jobs | Celery, RQ ou Arq |
| Storage | S3 compatível |
| Observabilidade | OpenTelemetry + Sentry |
| Pagamentos | Mercado Pago/Pix + app stores |
| WhatsApp | WhatsApp Business Platform |

## NFRs críticos

- Home P95 < 2s com cache quente
- Monitor P95 < 2,5s no mobile
- API ≥ 99,5% no MVP
- TLS obrigatório
- rate limit por IP/usuário
- logs sem CPF/telefone em claro
- fallback para dados oficiais em cache
- `model_version` presente em snapshots ALEQIA D

## Casos de teste críticos preservados

- usuário free não recebe número bloqueado
- pagamento falho não libera entitlement
- jogo Lotofácil com 14 ou 21 dezenas é inválido
- resultado com dezenas repetidas é rejeitado
- conferidor calcula hits corretamente
- WhatsApp não envia sem opt-in
- backtest não usa concurso futuro
