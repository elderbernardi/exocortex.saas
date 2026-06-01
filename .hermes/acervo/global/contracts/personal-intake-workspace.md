
---
title: Personal Intake Workspace
created: 2026-05-30
updated: 2026-05-30
nature: instrucoes
kind: contract
scope_mode: global
scope_slug: null
applies_to: [exocortex, hermes, acervo, intake, inbox, multichannel]
authority: canonical
operational_mode: blocking
stability: experimental
sources:
  - user:2026-05-30-intake-design
derived_from: []
confidence: high
promotion_policy: none
upstream:
  source_skill: exocortex/personal-intake-workspace
  assumed_version: 1.0.0
  coupling: adapter-only
tags: [intake-workspace, inbox, ingestion, reproducibility]
---

# Personal Intake Workspace

## Decisão

O Exocórtex recebe arquivos e mídias por uma área operacional `_inbox/`, não por escrita direta no Acervo semântico.

O Acervo continua sendo a memória curada. `_inbox/` guarda bruto, extração e roteamento.

## Contrato

1. Todo intake vive em `~/.hermes/acervo/_inbox/{intake_id}/`.
2. O diretório contém `original/`, `derived/`, `manifest.json`, `routing.json` e `log.json`.
3. O original é preservado.
4. O intake registra hash, MIME, tamanho, canal e status.
5. A triagem precede qualquer promoção semântica.
6. Upload bruto não entra direto em `knowledge/`, `context/`, `contracts/` nem páginas equivalentes.
7. Drive, Docs e equivalentes não são inbox primária; são workspace/publicação.
8. A arquitetura alvo é `USER -> GUI -> SERVER -> HERMES`.
9. A capability deve ser reproduzível em outro Exocórtex-Hermes.

## Estrutura

```text
~/.hermes/acervo/_inbox/{intake_id}/
├── original/
├── derived/
├── manifest.json
├── routing.json
└── log.json
```

## IntakeEnvelope mínimo

```json
{
  "intake_id": "int_YYYYMMDD_HHMMSS_slug",
  "channel": "telegram|whatsapp|email|webhook|api_server|dashboard|cli",
  "received_at": "ISO-8601",
  "content_type": "document|image|audio|video|zip|link|text",
  "original_filename": "...",
  "mime_type": "...",
  "local_cached_path": "...",
  "user_caption": "...",
  "correlation_id": "...",
  "session_ref": "..."
}
```

## Promoção

Promoção semântica só ocorre quando o sistema consegue responder:

- isso tem valor cognitivo durável?
- qual escopo?
- qual diretório funcional?
- qual Nature/kind?

Sem essas respostas, o material permanece em `_inbox/`.

## Critérios de aceite

- Existe uma `_inbox/` autocontida e separada do Acervo semântico.
- Cada intake possui manifesto e roteamento.
- O original foi preservado.
- A extração gerou texto utilizável quando aplicável.
- A promoção cria página semântica apenas em microverso existente e atualiza index/log.
