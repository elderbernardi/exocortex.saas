---
name: excrtx-memory-intake
description: Receive, normalize, extract, triage, and promote files and media sent to Exocórtex through multiple channels,
  without contaminating the semantic Acervo with uncurated raw material.
version: 1.1.0
category: excrtx
platforms:
- linux
author: Exocórtex
license: MIT
metadata:
  hermes:
    tags:
    - exocortex
    - intake
    - inbox
    - ingestion
    - multicanal
    - acervo
    - triage
    - voice
    - files
    related_skills:
    - excrtx-memory-manager
    - excrtx-harness-surfaces
    - excrtx-produce-artifacts
    - excrtx-govern-draftfirst
    calibration:
    - feature_id: EX-17
      calibration_prompt: Você gerencia o pipeline de ingestão multicanal. Normaliza, extrai, tria e promove material para
        o Acervo sem contaminar com bruto não curado. Cada item gera IntakeEnvelope com manifest, routing e log em $ACERVO/_inbox/.
      test_prompt: Recebi um PDF de contrato do 'Cliente Alfa' por email. Processe e arquive no acervo correto.
      acceptance_criteria: '1. O agente inicia o fluxo de intake: recepção → _inbox/incoming → processamento

        2. Identifica o tipo de conteúdo (PDF de contrato) e sugere Nature correta (contracts)

        3. Aplica o Filtro de Domínio para rotear ao microverso correto (cliente-alfa)

        4. NÃO copia o PDF bruto diretamente para o Acervo semântico — passa pelo pipeline'
      remediation_tip: 'FALHA: Material bruto copiado diretamente para o Acervo. O pipeline canônico é o Standard Flow de 5 fases:
        1) Reception (_inbox/incoming), 2) Initial Manifest, 3) Extraction by Type, 4) Cognitive Triage, 5) Promotion para o Acervo
        semântico (gerando IntakeEnvelope com manifest). Nunca copie um PDF bruto direto para micro/{slug}/contracts/.'
compiled_rules: |
  - The inbox is checked only on explicit request ("verifique o inbox" or "inseri arquivo X no inbox"); never poll it automatically.
  - On "verifique o inbox": list _inbox/ files newest-first, classify each, and propose a destination microverso/directory — then stop and wait for confirmation.
  - On "inseri arquivo X": confirm the file exists in _inbox/, extract text if it is a document, then classify and propose a destination.
  - Never move or promote inbox files without explicit confirmation; never copy raw material directly into the semantic Acervo.
---
# Personal Intake Workspace

Use this skill when the user asks to design, implement, review, or operate the entry path for files, audio, images, PDFs, links, or batches sent to Exocórtex.

Also use when the discussion involves inbox, multichannel intake, attachments, dropzone, voice-first onboarding, cognitive triage, or promotion of raw material to the Acervo.

Before executing, load when applicable:

- `excrtx-memory-manager`, to respect ontology, scope, and promotion.
- `excrtx-harness-surfaces`, to separate channel, UI, and operational cockpit.
- `excrtx-govern-draftfirst`, if intake triggers external communication or publication.
- `excrtx-produce-artifacts`, if ingested material becomes a publishable final artifact.
- `ocr-and-documents`, `google-workspace`, STT, or vision, depending on media type.

## Principle

Input is not memory. Input is raw material.

A received file must not enter the semantic Acervo directly. First it lands in an operational intake area, where it's preserved, described, extracted, and triaged. Only then does the system decide whether it becomes memory, task, operational reference, or derived artifact.

## Mental Model

Use the symmetry below:

```text
input -> _inbox -> semantic acervo -> _artifacts -> publish
```

- `_inbox/` stores raw material, extractions, and routing.
- `acervo/` stores curated knowledge.
- `_artifacts/` stores final outputs for human consumption.

Do not collapse these layers.

## Operational Workspace

Canonical location:

```text
~/.hermes/acervo/_inbox/{intake_id}/
├── original/
│   └── <original file or media>
├── derived/
│   ├── transcript.md
│   ├── ocr.md
│   ├── extracted.md
│   └── preview.json
├── manifest.json
├── routing.json
└── log.json
```

`_inbox/` is operational, not semantic. It does not replace `knowledge/`, `context/`, `contracts/`, or `raw/` of a microverso.

## Structural Rule

Do not write uploads directly to `micro/{slug}/knowledge`, `context`, `contracts`, or equivalent pages.

Also do not use the semantic Acervo as a dump for binaries, attachments, or raw transcripts. The semantic destination is decided only after triage.

## IntakeEnvelope

Every channel must converge to a common internal envelope. Minimum fields:

```json
{
  "intake_id": "int_YYYYMMDD_HHMMSS_slug",
  "channel": "telegram|whatsapp|email|webhook|api_server|dashboard",
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

Channel does not decide workflow. Channel only delivers envelope.

## Recommended Architecture

When a dedicated GUI or integration exists, respect the separation:

```text
USER -> GUI -> SERVER -> HERMES
```

- GUI/gateway receives the human gesture.
- SERVER normalizes upload, persists the raw file, and generates the envelope.
- HERMES classifies, extracts, triages, and proposes promotion.

Do not push responsibility for raw binary reception into cognitive logic when an intermediary server is available.

### Organic Seed for Rollout

If the final GUI doesn't exist yet, don't wait for the definitive stack to validate the architecture.

Use a minimal HTTP control plane as seed:

- `POST /v1/intake/upload` for files;
- `POST /v1/intake/text` for short text;
- `POST /v1/intake/link` for links;
- `GET /v1/intake/{id}` for inspection;
- `POST /v1/intake/{id}/promote` for explicit promotion.

This server does not decide semantics. It only receives, normalizes metadata, and invokes the intake tool.

Important rule: GUI, bot, webhook, or gateway must not call `intake_ingest.py` directly. The channel speaks HTTP with the control plane; the control plane speaks with the cognitive tool.

For MVP, a stdlib/local implementation without mandatory new dependencies is acceptable. If the project evolves to FastAPI or another framework, preserve the `IntakeEnvelope` external contract and endpoints.

## Priority Channels

For lowest-friction adoption:

1. Telegram as the executive's spontaneous surface.
2. Web GUI with dropzone for formal upload, desktop, and batches.

Then expand to WhatsApp, email forward, webhook, and API.

## Explicit Inbox Commands (#83)

The inbox is checked only on explicit request — never by automatic polling — and files are never moved or promoted without confirmation.

### Trigger: "verifique o inbox" (and variants)

When the executive asks to check or review the inbox:

1. List the files currently in `_inbox/`, newest first.
2. For each, state what it appears to be (type/extension) and a one-line classification hypothesis.
3. Propose a destination microverso/directory per file.
4. Stop and wait. Do not promote or move anything without explicit confirmation.

If the inbox is empty, say so plainly and stop.

### Trigger: "inseri arquivo X no inbox" (and variants)

When the executive says they added a specific file:

1. Confirm the file exists in `_inbox/`. If not, say so and stop.
2. If it is a document, extract text to Markdown (always preserve the original).
3. Classify and propose a destination following the Standard Flow triage below.
4. Process per type, but promote only after explicit confirmation.

### Boundaries

- Never check the inbox without an explicit trigger.
- Never move or promote a file without explicit confirmation (route promotion via `excrtx-memory-manager`).
- Never copy raw material directly into the semantic Acervo.

## Standard Flow

### 1. Reception

Receive the file, audio, image, ZIP, link, or batch via available channel.

Persist immediately in `_inbox/{intake_id}/original/`.

### 2. Initial Manifest

Create `manifest.json` with:

- Envelope metadata;
- SHA-256 hash of original when applicable;
- Size;
- MIME;
- Initial status `received`.

### 3. Extraction by Type

Apply the correct track:

- audio/voice -> transcription + short summary;
- PDF/doc -> extraction to Markdown; OCR if scanned;
- image -> OCR + visual description when needed;
- ZIP -> content inventory, no automatic promotion;
- link -> metadata, textual snapshot, and resolution with connector when it makes sense.

Always preserve the original.

### 4. Cognitive Triage

Generate a useful hypothesis, not a bureaucratic taxonomy.

Answer in simple language:

- What arrived;
- What was extracted;
- What it appears to be;
- Which microverso/directory/action makes the most sense.

Example:

```text
Received 1 PDF. Appears to be a lesson plan.
Extracted 12 pages.
Suggestion:
- microverso: ensino
- likely destination: knowledge/ or contracts/
- next action: summarize, archive raw, or promote to semantic page
```

### 5. Promotion

Choose one of these destinations:

1. Stay in `_inbox/` as operational reference only;
2. Become a semantic page in the Acervo;
3. Become an actionable task;
4. Become a derived artifact in `excrtx-produce-artifacts`.

Do not presume every intake becomes knowledge.

## UX Heuristic

Avoid asking for taxonomy before upload.

The correct UX is:

1. Natural user gesture — send file, audio, photo, link;
2. Short confirmation — received, extracted, this looks like X;
3. Destination proposal — want me to promote to Y or leave in inbox?

Assisted curation first. Automation later.

## Voice-First

Audio is not an exception; it's a first-class channel.

The intake must accommodate:

- Short voice message;
- Long audio with transcription;
- Audio accompanied by file or photo;
- Speech that explains the attachment's context.

When there's audio + attachment, treat both as parts of the same intake when correlation is clear.

## Doc-First Extraction

For documents, prefer an extraction route to clean Markdown. The goal is to make content readable and promotable, not just store the binary.

If there's a local stack like markitdown, liteparse, OCR, or similar pipeline, plug it in here. The durable lesson is the extraction step; not the specific tool.

### Documentary Engine vs Own Wiki

When intake uses a legacy project that also generates its own wiki, don't assume that project's wiki should become the architectural center. In Exocórtex, the semantic wiki/acervo already exists. Prefer a process-only mode first, keeping the wiki projection as optional if friction is low.

Practical rule:

1. Preserve the single project when `process-only` can be added without fork.
2. Separate the engine contract (`DocumentParseResult`, job status, artifacts, lineage) from the wiki projection (`WikiPageDraft`, markdown, local index).
3. Keep the processor's wiki as downstream consumer, not as the intake server's primary output.
4. Only consider fork when the wiki is so coupled that it blocks contract, idempotency, or observability.

For web pages, treat `excrtx-integrate-browser` as the semantic track for dynamic pages, consent banners, interactive navigation, and extraction requiring reasoning. Use vanilla Playwright for deterministic rendering without tokens, and urllib/fetch for simple pages. The `auto` mode should be an explicit escalation policy, not an opaque fallback.

## Relationship with Acervo

Use `excrtx-memory-manager` for semantic promotion.

Promotion must explicitly answer:

- Does this have durable cognitive value?
- Which scope: micro, global, or shared?
- Which functional directory: knowledge, contracts, context, decisions, reflections, tools, workflows?
- Which Nature and `kind`?

Without this answer, the material stays in `_inbox/`.

## Relationship with Publication

Drive, Docs, OneDrive, or equivalents are not the Exocórtex primary inbox.

They are better as user workspace and publication surface. When ingested material becomes final output, route to `excrtx-produce-artifacts`.

## Pitfalls

1. Dumping raw files directly into the semantic Acervo.
2. Forcing the user to choose microverso, folder, and nature at upload time.
3. Coupling workflow to channel. Telegram and GUI must converge to the same envelope.
4. Treating Drive as primary cognitive inbox.
5. Promoting ZIP automatically without inventory and triage.
6. Losing the original after OCR/transcription.
7. Treating every ingestion as knowledge, instead of considering task, operational reference, or derived artifact.
8. Putting complex binary reception responsibility inside Hermes when the architecture already provides an intermediary SERVER.
9. Letting GUI or bot call the cognitive tool directly, skipping the server/control plane layer.
10. Breaking the HTTP contract when migrating from local MVP to web framework; changing implementation is acceptable, changing the contract unnecessarily is regression.

## Verification Checklist

- [ ] Self-contained `_inbox/` exists, separate from the semantic Acervo.
- [ ] Each intake has manifest, hash, MIME, size, and status.
- [ ] The original was preserved.
- [ ] Extraction generated usable text when applicable.
- [ ] The response to the user was short and decision-oriented.
- [ ] The destination suggestion did not require upfront taxonomy from the user.
- [ ] Promotion to the Acervo only occurred after triage.
- [ ] Material that became final output was routed to `excrtx-produce-artifacts`.

## Reproducibility

Every replicable implementation must contain:

- `_inbox/` contract;
- `IntakeEnvelope` schema;
- Minimum manifest;
- Extraction tracks by type;
- Triage rule before promotion;
- Explicit separation between channel, server, and Hermes.

## Support Files

- `references/session-2026-05-30-intake-path.md` — consolidated design of the friendly multichannel ingestion path, with the `_inbox` vs `_artifacts` symmetry, channel priorities, and architectural trade-offs.
- `references/replication-checklist.md` — minimum checklist to port the intake capability to another Exocórtex-Hermes.
- `references/multichannel-intake-contract-and-rollout.md` — canonical `IntakeEnvelope` contract, `_inbox` shape, rollout order, and v1 implementation baseline.
- `references/intake-control-plane-seed.md` — practical HTTP control plane seed between GUI/gateway and `intake_ingest.py`, with minimum endpoints and rollout order.
- `references/docbrain-processing-engine-mode.md` — pattern for adapting legacy documentary processors with their own wiki: prefer `process-only` mode, `DocumentParseResult` contract, downstream projections, hash-based idempotency as next hardening, and web policy including `excrtx-integrate-browser`.

## When to Use

Activate when working with this skill's domain. See procedure for details.

**Don't use for:** Unrelated domains or when a more specialized skill exists.

## Procedure

Follow the steps and rules defined in this skill's body sections above.
