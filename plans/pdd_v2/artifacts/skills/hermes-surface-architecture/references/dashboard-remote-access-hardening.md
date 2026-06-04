# Dashboard remote-access hardening

Use this note when the task is not just "what surfaces exist" but "how do we ship Hermes safely for a real operator/end user split?"

## Recommended split

- End user: Telegram gateway
- Operator: Hermes Dashboard with embedded TUI enabled
- Remote operator access: Tailscale first, SSH tunnel second

## Why this matters

Hermes Dashboard is not a harmless brochure UI. It can expose:
- sessions
- logs
- config
- skills/plugins
- key-management surfaces

That makes it an operator cockpit, not a public app.

## Durable launch pattern on Linux

First launch:
- `hermes dashboard --tui --no-open`
- let the web assets build if needed
- verify HTTP response and visible `CHAT` tab

Persistent launch after assets exist:
- `python -m hermes_cli.main dashboard --tui --no-open --skip-build`

Suggested systemd user-service shape:
- `Type=simple`
- `Restart=always`
- explicit `WorkingDirectory`
- explicit `HERMES_HOME`
- explicit `VIRTUAL_ENV`
- PATH including Hermes venv/bin

## Remote access policy

Preferred:
- keep dashboard on `127.0.0.1:9119`
- join the host to Tailscale
- enforce access via tailnet ACLs / device approval

Acceptable fallback:
- temporary SSH tunnel: `ssh -L 9119:127.0.0.1:9119 user@host`

Avoid recommending as default:
- public reverse proxy without strong access control
- public `0.0.0.0:9119`
- normalizing `--insecure` as a convenience flag

## Operator checklist

1. Dashboard process/service is running.
2. `http://127.0.0.1:9119/` responds locally.
3. `CHAT` tab is visible when `--tui` is enabled.
4. Public internet cannot reach port 9119.
5. Remote administration path is Tailscale or SSH only.
