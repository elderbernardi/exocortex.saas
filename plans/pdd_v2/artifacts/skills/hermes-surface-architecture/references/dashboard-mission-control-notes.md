# Hermes Dashboard / Mission Control notes

Condensed findings from repo/doc review around the video "How to Enable the TUI in the Dashboard: Session Recovery Tips & Prompts".

## Video-aligned facts

- Hermes Dashboard is an official first-party surface exposed by the native command `hermes dashboard`.
- The embedded chat/TUI inside the dashboard is opt-in.
- Enable it with:
  - `hermes dashboard --tui`
  - or `HERMES_DASHBOARD_TUI=1`
- Session recovery is a real workflow: resume from the Sessions view rather than assuming refresh lost state.

## Packaging model

### Native
- `hermes dashboard` is a native Hermes command.

### Native but optional
- Web stack dependencies are optional extras, not part of the minimum core footprint.
- PTY support for embedded chat is also an optional dependency path.
- Practical provisioning guidance: preinstall extras instead of relying on lazy-install during first run.

### Bundled plugin
- The dashboard has a first-party plugin architecture.
- Kanban is the reference example of a bundled dashboard plugin.
- Plugin assets are shipped in the wheel/package.

## Mission Control

Observed evidence did not support treating "Mission Control" as a separately documented first-class product surface.

Concrete signal found:
- references in dashboard auth/proxy handling mention `X-Forwarded-Prefix: /hermes (Mission Control deploys)`

Operational reading:
- "Mission Control" appears to describe a deployment/reverse-proxy environment around the dashboard rather than a distinct user-facing core module.
- Do not present it as a clearly separate built-in feature unless stronger product-level documentation is found.

## Platform caveat

- Dashboard web surface: generally fine cross-platform.
- Embedded `/chat` pane: special case.
- For predictable embedded chat behavior, prefer Linux, macOS, or WSL2.
- On Windows-native, do not make embedded dashboard chat the primary executive path.

## Recommended delivery pattern

For low-friction executive delivery:

1. Primary surface: messaging gateway (default: Telegram)
2. Secondary/operator surface: Hermes Dashboard
3. Operator-only surface: CLI/TUI and, if useful, embedded dashboard chat

Rationale:
- minimizes onboarding
- keeps session/log/config visibility for the operator
- avoids exposing fragile or high-friction technical surfaces to the executive
