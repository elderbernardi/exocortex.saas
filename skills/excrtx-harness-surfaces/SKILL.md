---
name: excrtx-harness-surfaces
description: Decide, explain, and package Hermes user-facing surfaces (gateways, web
  UI, dashboard, TUI, embedded chat) for low-friction delivery, especially when the
  operator and end user are different people.
version: 1.0.0
category: excrtx
platforms:
- linux
metadata:
  hermes:
    tags:
    - exocortex
    - harness
    - surfaces
    related_skills:
    - excrtx-harness-delivery
    - excrtx-govern-draftfirst
    calibration:
    - feature_id: EX-35
      calibration_prompt: Você deve garantir que as operações e regras da skill Surface
        Architecture (excrtx-harness-surfaces) estão totalmente ativas no seu comportamento
        e integridade.
      test_prompt: Verifique se a skill define Gateway, UI/Web e TUI como superfícies.
      acceptance_criteria: O agente deve demonstrar de forma clara e factual que compreende
        as regras e procedimentos da skill Surface Architecture.
      remediation_tip: Certifique-se de que a documentação e os limites da skill Surface
        Architecture em seu SKILL.md estão sendo estritamente seguidos.
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

> **Delivery architecture** (OAuth connectors, artifact publishing, CLI APIs, runtime/workspace separation, contingency surfaces) is covered by `excrtx-harness-delivery`.

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

- `references/dashboard-mission-control-notes.md` — Hermes Dashboard, embedded chat, Mission Control findings
- `references/dashboard-tui-activation.md` — operator checklist for `hermes dashboard --tui`
- `references/dashboard-remote-access-hardening.md` — systemd persistence, localhost binding, Tailscale-first access
- `references/hermes-remote-file-surfaces-github-landscape.md` — GitHub research taxonomy for remote-file projects
- `references/workspace-ui-bases.md` — workspace UI decision notes and local discovery rules

> For delivery references (artifact publishing, CLI API contracts, runtime layout, contingency activation), see `excrtx-harness-delivery`.

## When to Use

Activate when:
- Choosing between gateway, UI, and TUI options in Hermes
- Explaining what is native vs optional vs plugin-based
- Designing a low-friction delivery model for a non-technical end user
- Deciding primary surface (dashboard, Telegram, custom UI, etc.)
- Separating operator tooling from end-user experience
- Packaging Hermes for executive handoff

**Don't use for:** Tool/skill development (use `excrtx-harness-tooldev`). OAuth setup (use `excrtx-integrate-oauth`). Artifact content generation (use `excrtx-produce-artifacts`). Memory/Acervo management (use `excrtx-memory-manager`).

## Procedure

1. **Classify the layers:** Separate gateway (transport), UI/web (browser), and TUI/CLI (operator) — never collapse them
2. **Recommend primary surface:** For non-technical executives → Telegram. For operators → Dashboard + CLI
3. **Assess dashboard needs:** Run `hermes dashboard --tui --no-open` to verify; confirm both HTTP endpoint (`http://127.0.0.1:9119/`) and `CHAT` tab render
4. **Apply security posture:** Dashboard bound to localhost. Remote access via Tailscale or SSH tunnel only. Never `--host 0.0.0.0` without secure transport
5. **Package for delivery:** Preinstall web dependencies, validate surface, create systemd service if durable. Use `--skip-build` after first successful build
6. **Structure response:** Short answer → terminology → recommendation → delivery guidance → verdict

## Verification

- [ ] Response separates gateway, UI, and TUI as distinct architectural layers
- [ ] Primary surface recommendation matches executive's technical profile
- [ ] Dashboard bound to localhost (not 0.0.0.0) in production config
- [ ] `http://127.0.0.1:9119/` responds AND `CHAT` tab is visible (if TUI enabled)
- [ ] Remote access uses Tailscale/SSH, not direct port exposure
- [ ] OAuth connectors use `connection_id`, never raw tokens
- [ ] Draft-First applied for irreversible actions (send, share, publish)
