# Dashboard TUI activation

Use this when the task is not just to explain Hermes Dashboard, but to actually leave the operator with a live embedded chat surface.

## Activation command

Preferred local launch:

`hermes dashboard --tui --no-open`

Why this variant:
- enables the embedded chat tab explicitly
- avoids browser auto-open side effects during automation or remote setup
- works cleanly for service/background patterns

## First-run behavior

Expect the first launch to behave like provisioning:
- the web UI may build automatically if the dist assets are missing
- a successful build is not the same as a successful running dashboard

Do not stop at the build log.

## Validation checklist

Mark the task complete only after all three checks pass:

1. Process stays alive after launch
- confirm the `hermes dashboard --tui --no-open` process is still running

2. Local endpoint answers
- confirm `http://127.0.0.1:9119/` responds

3. Embedded chat is exposed in the UI
- confirm the left navigation includes `CHAT`
- opening `CHAT` should show the embedded terminal surface

## Recommended operator workflow

1. Launch in background/service mode
2. Wait for the process to stabilize
3. Probe the localhost endpoint
4. Open the dashboard and verify `CHAT`
5. Only then report that Dashboard+TUI is enabled

## Reporting guidance

For executive-facing delivery, separate these statements:
- "Dashboard is running"
- "Embedded chat/TUI is enabled"

Do not collapse them into one sentence unless both were explicitly validated.
