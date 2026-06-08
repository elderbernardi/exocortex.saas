---
name: excrtx-harness-surfaces
description: Decide, explain, and package Hermes user-facing surfaces (gateways, web UI, dashboard, TUI, embedded chat) for low-friction delivery, especially when the operator and end user are different people.
version: 1.0.0
---

# Hermes Surface Architecture

Use this skill when the task is about:
- choosing between gateway, UI, and TUI options in Hermes
- explaining what is native vs optional vs plugin-based in the Hermes surface area
- designing a low-friction delivery model for a non-technical end user
- deciding whether dashboard, embedded chat, Telegram, or a custom UI should be primary
- separating operator tooling from end-user experience
- surveying GitHub projects that expose Hermes through desktop, web, SSH, gateway, or remote-file surfaces

## Core distinction

Do not collapse these into one bucket:

1. Gateway
- The delivery channel the end user actually talks to.
- Examples: Telegram, Discord, Slack, email, SMS, Matrix, etc.

2. UI / Web surface
- A browser interface for configuration, monitoring, sessions, logs, plugins, or chat.
- Examples: Hermes Dashboard, Open WebUI, a custom app over the API.

3. TUI / operator console
- A terminal-first interface for technical operators.
- Example: Hermes CLI / TUI.

When the user asks for “gateway with UI/TUI”, answer by separating these layers first. That avoids mixing transport with interface.

## Default recommendation for executive delivery

If the goal is adoption with minimal onboarding:

1. Make a familiar messaging app the primary user surface.
- Default recommendation: Telegram.
- Reason: lowest friction, mobile-native, notifications, no extra training.

2. Keep Hermes Dashboard as the operator cockpit or secondary surface.
- Use it for sessions, logs, config, cron, plugin tabs, and supervision.
- Do not make it the primary interface for low-technical users unless there is a strong reason.

3. Keep CLI/TUI for the administrator/operator.
- Do not expose terminal-first workflows to the executive unless they explicitly want them.

This separation should be explicit in the answer.

## Canonical positioning of Hermes Dashboard

Treat Hermes Dashboard as:
- official and native to the Hermes ecosystem
- invoked by the native command `hermes dashboard`
- not part of the bare-minimum install footprint
- dependent on optional extras for reliable operation

Important nuance:
- The runtime may lazy-install web dependencies in some environments.
- For production delivery, do not rely on lazy-install as the provisioning strategy.
- Preinstall the needed extras and validate the surface before handoff.

## Embedded chat / TUI inside the dashboard

The dashboard can expose the real Hermes TUI inside the browser.

Activation:
- `hermes dashboard --tui`
- or `HERMES_DASHBOARD_TUI=1`

Operational pattern:
- Prefer `hermes dashboard --tui --no-open` when enabling it on a prepared machine.
- Treat first launch as a provisioning step, not just a runtime step: the web UI may build automatically on first run if assets are not present.
- After the first successful build, prefer a persistent launch command with `--skip-build` to avoid unnecessary rebuilds during routine restarts.
- If you need a durable operator surface, persist it as a user service when the host supports `systemd --user`, then verify both the HTTP endpoint and the presence of the `CHAT` tab.
- Verify success with two checks, not one: (1) `http://127.0.0.1:9119/` responds, and (2) the dashboard navigation shows `CHAT`.
- A good Linux service pattern is `python -m hermes_cli.main dashboard --tui --no-open --skip-build` with `Restart=always`, `WorkingDirectory` pointing at the Hermes repo/venv, and `HERMES_HOME` exported explicitly.

Position it correctly:
- native feature
- opt-in, not default
- useful for operator recovery and continuity
- not the primary recommendation for non-technical end users

## Security posture for dashboard delivery

Treat Hermes Dashboard as a sensitive operator surface.

Default rules:
- keep it bound to localhost unless there is a deliberate secure access layer
- do not expose port `9119` directly to the public internet
- do not normalize `--insecure` or broad `--host 0.0.0.0` binds as a convenience shortcut

Remote access recommendation:
- for continuous remote administration, prefer Tailscale as the default secure transport
- SSH tunnel is acceptable for temporary/operator-only access
- phrase this as a setup requirement, not a nice-to-have, when the environment contains real sessions, logs, config, or keys

If the user is packaging Hermes for an executive:
- executive-facing surface stays in Telegram (or equivalent gateway)
- dashboard stays private and operator-facing
- remote operator access goes through Tailscale/SSH, not public exposure

## Per-user OAuth connectors for web users

When the goal is to let a non-technical web user click "Connect Google" or
"Connect Microsoft 365" and then have Hermes act on that account, do **not**
architect it as "the user gives OAuth tokens to Hermes".

Use this separation instead:

1. Web app / connector UI
- Owns the "Connect account" UX.
- Redirects the user to Google/Microsoft OAuth.
- Shows connection status, scopes, reconnection, and approvals.

2. Connector backend / OAuth broker
- Receives the OAuth callback.
- Exchanges `code` for tokens.
- Stores refresh tokens encrypted.
- Refreshes access tokens when needed.
- Maps each connection to `user_id`, `workspace_id`, and provider account.

3. Hermes-facing integration layer
- Exposes semantic tools via MCP or a thin API facade.
- Hermes passes `connection_id` / user context, never raw tokens.
- The integration layer resolves the connection, loads tokens, enforces policy,
  calls Google/Microsoft, and returns sanitized results.

Recommended runtime path:

Hermes -> MCP/API connector facade -> connector backend/vault -> Google or Microsoft

### Preferred Hermes packaging

For Hermes itself, prefer an MCP server as the connector surface.

Why:
- keeps OAuth/token handling outside Hermes
- makes tools first-class without patching Hermes core
- supports swapping native adapters vs aggregators later
- preserves Draft-First and approval workflows cleanly

Typical MCP/API tool shape:
- `list_connected_accounts`
- `search_emails`
- `create_email_draft`
- `send_email_draft`
- `list_calendars`
- `create_calendar_draft`
- `confirm_calendar_event`

### Security rule

Hermes should operate on **connection references**, not credentials.

Good:
- `connection_id=conn_google_123`
- `account_label=elder@...`
- `capabilities=[mail, calendar]`

Bad:
- passing `access_token` or `refresh_token` into Hermes config, env, prompts,
  memory, tool output, or logs

### Approval model

If a connector can write or send, model it in Draft-First stages:
- read operations may be automatic
- reversible creation should produce drafts/previews
- irreversible actions (`send`, final calendar creation, sharing docs) should
  require explicit approval

## Hermes runtime vs Exocórtex workspace

When packaging Hermes as the engine behind Exocórtex, keep these layers separate:

```bash
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"          # Hermes runtime: config, auth, sessions, logs, skills, profiles
EXOCORTEX_HOME="${EXOCORTEX_HOME:-$HOME/exocortex}" # Exocórtex workspace/cockpit
ACERVO="${ACERVO:-$EXOCORTEX_HOME/acervo}"          # canonical cognitive archive
```

Recommended production shape:

- Keep Hermes runtime in `~/.hermes`.
- Keep Exocórtex scaffold and Acervo in `~/exocortex`.
- Use `~/exocortex/acervo` as canonical Acervo path.
- If compatibility is needed, make `~/.hermes/acervo` a symlink to `$ACERVO`, not the conceptual source of truth.
- Prefer running production Hermes with cwd at `$EXOCORTEX_HOME`; do not use `~/.hermes` as routine cwd.

Why cwd matters:

- CLI Hermes local uses the directory from which `hermes` was launched.
- Gateway/messaging uses `terminal.cwd` from `config.yaml`.
- Relative paths, broad file searches, local project rules, and generated helper files follow that workspace.

Pitfalls:

- Do not move auth, config, logs, sessions, skills, profiles, Hindsight config, or provider state into `~/exocortex`; those remain Hermes runtime.
- Do not infer the Acervo from `$HERMES_HOME/acervo` in new Exocórtex skills or scripts; resolve `ACERVO` or `EXOCORTEX_HOME`.
- Do not migrate an existing real `~/.hermes/acervo` directory without backup or explicit migration flag.
- Historical logs/backups may contain old paths; mark them as legacy rather than rewriting history.

Reference: `references/exocortex-home-layout.md`.

## Opt-in contingency surfaces

When introducing a fallback, degraded, or budget-emergency mode, do not make the mode default just because it is operationally useful.

Use this rule:
- normal path stays the default
- contingency path is explicit and opt-in
- CLI flag and chat command should mirror the same intent

Preferred packaging pattern:
- CLI activation via a named flag such as `--imbroke`
- chat/gateway activation via a parallel operational command such as `/xc imbroke`
- write/apply actions must require the explicit contingency activation, not merely the presence of credentials or a provider key
- read-only/reporting may run without activation when the goal is inspection rather than switching modes

Why:
- preserves the main product posture
- prevents fallback logic from silently replacing the intended primary path
- makes emergency behavior easy to invoke without normalizing it as baseline behavior

Pitfalls:
- do not auto-enable a fallback provider during setup just because `OPENROUTER_API_KEY` or equivalent credentials exist
- do not let `--apply` or equivalent write actions run unless the contingency flag is present
- do not document a chat command without mirroring it in the CLI/API surface; operator and gateway semantics should stay aligned

Reference: `references/contingency-surface-activation.md`.

## Local CLI APIs for sibling engines

When Hermes will operate a sibling local project as an engine, do not default to HTTP just because the word “API” appears. If Hermes and the engine share a workspace and the interaction is local, prefer a machine-oriented CLI API:

```bash
<tool> api <resource> <action> --output json
```

Keep the human CLI separate from the machine surface. For example, `docbrain ingest file.pdf` can remain the operator command while `docbrain api parse create --input file.pdf --output json` becomes the Hermes contract.

Agent-safe CLI API rules:
- stdout contains only JSON
- logs/progress go to stderr
- every response uses a stable envelope with `ok`, `api_version`, `command`, `request_id`, `job`, `data`, `warnings`, and `errors`
- complex calls accept JSON via `--request -`
- idempotent behavior is the default for agent calls
- large fields, such as raw extracted text, are opt-in via `--include`
- tests execute the real CLI as a subprocess and parse stdout as JSON to catch accidental human output

Reference: `references/local-cli-api-contracts.md`.

## Artifact publishing for final deliverables

When the user asks how Hermes should deliver final generated artifacts — PDFs, docs, spreadsheets, ZIPs, HTML, images, datasets — separate code publication from artifact delivery.

Default architecture:

1. Code repositories go through GitHub.
- Use branch/commit/PR/release workflows when the output belongs to a repo.
- Do not use GitHub as the default delivery UX for ordinary documents unless the artifact is part of a software release.

2. User-facing final artifacts go through an Artifact Publisher.
- The agent should call a single abstraction such as `publish_artifact(path, kind, title, audience, ttl, visibility)`.
- The publisher returns an artifact receipt: id, filename, MIME, size, SHA-256, expiry, signed download URL, local manifest path, and delivery status.
- The model should not reason directly about S3/R2/MinIO/gateway internals during normal work.

3. Delivery should be hybrid.
- If the gateway supports native file upload and can read the file, send the attachment.
- Always prefer or include a signed URL fallback for remote gateways, sandboxed terminal backends, large files, and unsupported platforms.
- For multiple files, bundle a ZIP and include individual artifact receipts only when useful.

4. Use S3-compatible object storage as the default backend.
- Cloudflare R2 is the preferred remote-friendly default.
- MinIO is the preferred self-hosted/local/institutional default.
- AWS S3 fits environments already committed to AWS.

5. Keep a local manifest.
- Store publication metadata under `~/.hermes/artifacts/{session_id}/{artifact_id}/`.
- Include original/bundled file, `manifest.json`, MIME, size, checksum, source session/job, delivery target, status, expiry, and revocation metadata.

Draft-First boundary:
- Ephemeral delivery back to the requesting user in the current channel can be treated as part of the requested artifact-generation task.
- Sharing with third parties, durable public links, Drive/Docs/Notion publication, or broader visibility requires Draft-First approval.

Security baseline:
- private bucket, short TTL, checksums, MIME sniffing, credential/system-path denylist, path traversal protection, per-user/profile/session prefixes, no full signed tokens in logs, and no storage credentials in prompts/memory/acervo.

Reference: `references/artifact-publishing-architecture.md`.

## Platform caveat: Windows

Be precise here.

- The dashboard web surface can work on Windows.
- The embedded `/chat` pane is the special case.
- For dependable embedded chat behavior, prefer Linux, macOS, or WSL2.

Do not oversell the embedded chat pane as a universal end-user surface on Windows-native setups.

## Mission Control handling

When “Mission Control” appears in videos or code references:
- do not assume it is a first-class end-user product or a native CLI command
- verify whether it is documented as a product surface, a deploy context, or an internal naming convention

If evidence only shows reverse-proxy or deploy references, say so plainly:
- “Mission Control appears to be a deployment/proxy context around the dashboard, not a clearly separate core feature.”

Do not promote it as a supported product layer without stronger evidence.

## Native vs optional vs bundled framing

Use this classification when explaining Hermes surfaces:

1. Native
- official Hermes commands and first-party surfaces
- example: `hermes dashboard`

2. Native but optional
- first-party capabilities that depend on optional extras or toggles
- example: dashboard web stack, PTY support, embedded dashboard chat

3. Bundled plugin
- shipped with the Hermes ecosystem/package but mounted through the dashboard plugin architecture
- example: Kanban tab/plugin

4. External or custom
- Open WebUI, custom frontends, custom dashboards, operator-specific wrappers

This framing is usually clearer than “built-in vs not built-in”.

## Recommended answer shape

For this class of request, structure the response in this order:

1. Short answer
- what is native
- what is optional
- what is plugin-based

2. Clarify terminology
- gateway vs UI vs TUI

3. Operational recommendation
- what should be primary for the executive
- what should remain operator-only

4. Delivery guidance
- what to preinstall
- what not to rely on at first run
- platform caveats

5. Verdict
- the stack you would actually ship

## Pitfalls

- Do not treat “dashboard exists” as proof that it should be the primary user interface.
- Do not assume video terminology maps 1:1 to official product packaging.
- Do not rely on lazy-install for executive-facing delivery.
- Do not blur channel transport and operator console into the same architectural category.
- Do not recommend embedded dashboard chat on Windows-native as the default executive path.
- Do not mark the setup complete just because the build finished; confirm the process stayed up, the local HTTP endpoint answered, and the `CHAT` tab rendered.
- Do not persist the dashboard by replaying the first-run build path forever; once assets exist, switch the durable service to `--skip-build`.
- Do not expose dashboard remote access by simply binding to all interfaces; require Tailscale or SSH tunneling in the recommended architecture.

## Support files

- `references/local-cli-api-contracts.md` — design pattern for machine-oriented local CLI APIs that Hermes can call as stable JSON contracts, including envelope shape, stdout/stderr discipline, idempotency defaults, and subprocess JSON-purity tests.
- `references/dashboard-mission-control-notes.md` — distilled findings on Hermes Dashboard, embedded chat, Mission Control references, and packaging nuances from repo/doc investigation.
- `references/dashboard-tui-activation.md` — operator checklist for enabling `hermes dashboard --tui`, handling first-run build behavior, and validating that embedded chat is actually live.
- `references/dashboard-remote-access-hardening.md` — deployment notes for systemd persistence, localhost binding, and Tailscale-first remote access.
- `references/artifact-publishing-architecture.md` — artifact delivery pattern for final user deliverables: GitHub for code, S3-compatible signed URLs + native gateway attachment fallback for docs/PDFs/spreadsheets/ZIPs/HTML.
- `references/hermes-remote-file-surfaces-github-landscape.md` — GitHub research taxonomy for Hermes remote-file projects: backend operators, workspace UIs, and runtime adapters, plus English query patterns that reduce repo-search noise.
- `references/workspace-ui-bases.md` — decision notes for choosing between Hermes workspace UIs, launch/verification notes for `pyrate-llama/hermes-ui`, and local discovery rules before cloning alternative surfaces.
