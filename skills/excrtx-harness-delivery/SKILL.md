---
name: excrtx-harness-delivery
description: Hermes delivery architecture — OAuth connectors, artifact publishing, local CLI APIs, runtime/workspace separation,
  and contingency surface activation.
version: 1.0.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - harness
    - delivery
    - oauth
    - artifacts
    - cli-api
    related_skills:
    - excrtx-harness-surfaces
    - excrtx-govern-draftfirst
    - excrtx-integrate-gdrive
    calibration:
    - feature_id: EX-53
      calibration_prompt: 'Você gerencia a arquitetura de delivery do Hermes: OAuth connectors, artifact publishing, local
        CLI APIs, separação runtime/workspace e ativação de superfícies de contingência.'
      test_prompt: O Telegram caiu e meu executivo precisa receber o relatório que está pronto. Qual é o plano de contingência?
      acceptance_criteria: '1. O agente identifica que o gateway primário está indisponível

        2. Propõe superfície de contingência (email, Discord, CLI local, Dashboard)

        3. Explica como ativar a superfície alternativa sem perder o artefato

        4. NÃO apenas diz ''espere o Telegram voltar'' — oferece alternativa acionável'
      remediation_tip: 'FALHA: Sem contingência para gateway indisponível. A delivery architecture exige superfícies alternativas:
        se Telegram cair, use email/Discord/CLI/Dashboard. O artefato pronto deve ser entregue por qualquer canal disponível.
        Verifique ''hermes gateway list'' para ver gateways ativos e rotas alternativas.'
---
# Hermes Delivery Architecture

Delivery patterns for how Hermes connects to external services, publishes artifacts to end users, and interfaces with sibling local engines.

## When to Use

Activate when:
- Designing OAuth connector flows for web users (Google, Microsoft 365)
- Deciding how Hermes publishes final deliverables (PDFs, docs, ZIPs)
- Building local CLI API contracts between Hermes and sibling engines
- Separating Hermes runtime (`$HERMES_HOME`) from Exocórtex workspace (`$EXOCORTEX_HOME`)
- Implementing contingency/fallback surface activation (`--imbroke`)

**Don't use for:** Choosing between gateway/UI/TUI surfaces (use `excrtx-harness-surfaces`). Tool governance (use `excrtx-govern-tools`). Google Drive integration (use `excrtx-integrate-gdrive`).

## Per-user OAuth connectors for web users

When the goal is to let a non-technical web user click "Connect Google" or
"Connect Microsoft 365" and then have Hermes act on that account, do **not**
architect it as "the user gives OAuth tokens to Hermes".

Use this separation instead:

| Layer | Responsibility |
|-------|---------------|
| **Web app / connector UI** | Owns "Connect account" UX, OAuth redirect, connection status, scopes, reconnection |
| **Connector backend / OAuth broker** | Receives OAuth callback, exchanges `code` for tokens, stores refresh tokens encrypted, maps to `user_id`/`workspace_id` |
| **Hermes integration layer** | Exposes semantic tools via MCP/API facade. Hermes passes `connection_id`, never raw tokens |

Runtime path: `Hermes -> MCP/API connector facade -> connector backend/vault -> Google or Microsoft`

### Preferred Hermes packaging

Prefer an MCP server as the connector surface:
- keeps OAuth/token handling outside Hermes
- makes tools first-class without patching Hermes core
- supports swapping native adapters vs aggregators later
- preserves Draft-First and approval workflows cleanly

Typical MCP/API tool shape:
- `list_connected_accounts`
- `search_emails` / `create_email_draft` / `send_email_draft`
- `list_calendars` / `create_calendar_draft` / `confirm_calendar_event`

### Security rule

Hermes operates on **connection references**, not credentials.

Good: `connection_id=conn_google_123`, `account_label=elder@...`, `capabilities=[mail, calendar]`
Bad: passing `access_token` or `refresh_token` into config, env, prompts, memory, tool output, or logs.

### Approval model

If a connector can write or send, model it in Draft-First stages:
- read operations may be automatic
- reversible creation → drafts/previews
- irreversible actions (`send`, final calendar creation, sharing docs) → explicit approval

## Hermes runtime vs Exocórtex workspace

Keep these layers separate:

```bash
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"          # runtime: config, auth, sessions, logs, skills, profiles
EXOCORTEX_HOME="${EXOCORTEX_HOME:-$HOME/exocortex}" # workspace/cockpit
ACERVO="${ACERVO:-$EXOCORTEX_HOME/acervo}"          # canonical cognitive archive
```

Recommended production shape:
- Hermes runtime in `~/.hermes`
- Exocórtex scaffold and Acervo in `~/exocortex`
- `~/exocortex/acervo` as canonical Acervo path
- `~/.hermes/acervo` as symlink to `$ACERVO` if needed (not source of truth)
- Production Hermes with cwd at `$EXOCORTEX_HOME` (not `~/.hermes`)

Why cwd matters:
- CLI Hermes local uses the launch directory
- Gateway/messaging uses `terminal.cwd` from `config.yaml`
- Relative paths, file searches, and generated files follow that workspace

## Opt-in contingency surfaces

When introducing a fallback, degraded, or budget-emergency mode, do not make it default.

| Rule | Implementation |
|------|---------------|
| Normal path is default | Contingency is opt-in only |
| CLI activation | Named flag like `--imbroke` |
| Chat activation | Parallel command like `/xc imbroke` |
| Write actions | Require explicit contingency flag |
| Read-only/reporting | May run without activation |

## Local CLI APIs for sibling engines

When Hermes operates a sibling local project, prefer machine-oriented CLI API over HTTP:

```bash
<tool> api <resource> <action> --output json
```

Agent-safe CLI API rules:
- stdout = only JSON; logs/progress → stderr
- Stable envelope: `ok`, `api_version`, `command`, `request_id`, `job`, `data`, `warnings`, `errors`
- Complex calls accept JSON via `--request -`
- Idempotent by default for agent calls
- Large fields opt-in via `--include`
- Tests run real CLI as subprocess and parse stdout as JSON

## Artifact publishing for final deliverables

Separate code publication from artifact delivery.

| Channel | When to Use |
|---------|------------|
| **GitHub** | Code repos: branch/commit/PR/release workflows |
| **Artifact Publisher** | User-facing finals: PDFs, docs, spreadsheets, ZIPs, HTML, images |

Artifact Publisher contract:
- Agent calls: `publish_artifact(path, kind, title, audience, ttl, visibility)`
- Returns receipt: id, filename, MIME, size, SHA-256, expiry, signed URL, local manifest, delivery status
- Model never reasons about S3/R2/MinIO internals directly

Delivery is hybrid:
- Native gateway file upload when supported
- Signed URL fallback for remote gateways, sandboxed backends, large files
- Bundle ZIP for multiple files

Backend preference: Cloudflare R2 (remote) > MinIO (self-hosted) > AWS S3 (existing AWS).

Local manifest at `~/.hermes/artifacts/{session_id}/{artifact_id}/`.

Draft-First boundary:
- Ephemeral delivery to requesting user in current channel → automatic
- Sharing with third parties, public links, Drive/Docs → Draft-First approval

Security baseline: private bucket, short TTL, checksums, MIME sniffing, credential denylist, path traversal protection, per-user prefixes, no signed tokens in logs.

## Pitfalls

- **Token leakage:** Never pass `access_token` or `refresh_token` into Hermes config, env, prompts, memory, or logs. Use `connection_id` references.
- **Runtime/workspace confusion:** Do not move auth, config, logs, sessions, skills, or Hindsight config into `~/exocortex`; those stay in `~/.hermes`.
- **Contingency auto-enable:** Do not auto-enable a fallback provider just because `OPENROUTER_API_KEY` exists. Require explicit `--imbroke` flag.
- **CLI API stdout pollution:** Human-readable output in stdout breaks agent JSON parsing. Route logs to stderr.
- **GitHub as doc delivery:** Do not use GitHub as default delivery UX for ordinary documents — only for software releases.
- **Acervo path inference:** Do not resolve Acervo from `$HERMES_HOME/acervo` in new scripts; use `$ACERVO` or `$EXOCORTEX_HOME/acervo`.

## Support files

- `references/artifact-publishing-architecture.md` — artifact delivery pattern
- `references/local-cli-api-contracts.md` — CLI API envelope and testing patterns
- `references/exocortex-home-layout.md` — runtime vs workspace separation
- `references/contingency-surface-activation.md` — opt-in fallback activation

## Procedure

1. **Classify delivery domain:**

   | IF request mentions... | THEN route to... |
   |------------------------|-------------------|
   | "Connect Google/Microsoft", OAuth, tokens | → **OAuth connectors** section |
   | PDF, doc, ZIP, file delivery, publish | → **Artifact publishing** section |
   | CLI API, JSON contract, sibling engine | → **Local CLI APIs** section |
   | `$HERMES_HOME`, `$EXOCORTEX_HOME`, workspace | → **Runtime vs workspace** section |
   | fallback, `--imbroke`, contingency, budget | → **Contingency surfaces** section |

2. **OAuth connector flow:**
   - Verify connector exists: `hermes mcp list | grep connector`
   - Use `connection_id` references, never raw tokens
   - Enforce Draft-First for write/send: `create_email_draft` before `send_email_draft`

3. **Artifact publishing flow:**
   - Call `publish_artifact(path, kind, title, audience, ttl, visibility)`
   - Verify receipt contains SHA-256 + signed URL
   - Prefer gateway file upload; fall back to signed URL

4. **CLI API flow:**
   - Route through `<tool> api <resource> <action> --output json`
   - Validate stdout is pure JSON: `<tool> api ... | python -m json.tool`
   - Verify envelope contains `ok`, `api_version`, `data` fields

5. **Post-delivery:** Verify security posture — no tokens in logs, `$HERMES_HOME`/`$EXOCORTEX_HOME` separation intact

## Verification

- [ ] OAuth connectors use `connection_id`, never raw tokens
- [ ] Artifact publishing returns a receipt with SHA-256 and signed URL
- [ ] CLI API stdout contains only JSON, logs go to stderr
- [ ] `$HERMES_HOME` and `$EXOCORTEX_HOME` are separate, not mixed
- [ ] Contingency mode requires explicit `--imbroke` activation
- [ ] Draft-First applied for irreversible actions (send, share, publish)
