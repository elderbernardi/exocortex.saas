# Hermes workspace UI bases

Use this when the goal is a UI for operating a Hermes-managed workspace, especially file browsing and editing.

## Product framing

If Hermes should manage only the workspace layer, separate candidates by surface:

- `pyrate-llama/hermes-ui`
  - Best fit for `USER -> GUI -> SERVER -> HERMES`
  - Strongest current match for workspace operations and file editing
  - Web UI with workspace-aware file browser, in-place create/edit/rename/delete, folder creation, previews, uploads, terminal, chat, tasks

- `dodo-reach/hermes-desktop`
  - Best desktop reference for SSH-first host operations
  - Good for editing remote text files on the real host with conflict checks
  - Better as an operator workbench than as the base of a product UI

- `acegraphx/hermes-desktop-win`
  - Windows variant of the same SSH-first model
  - Strong for canonical Hermes files and wiki-style editing

- `fathah/hermes-desktop`
  - Better positioned as installer/admin surface than as a workspace-file operations UI

## Decision rule

If the user wants product/UI direction and the architecture keeps a server between GUI and Hermes, default to `hermes-ui` as the primary base. Treat the desktop apps as UX and operational references, not the main foundation.

## Practical launch notes for `pyrate-llama/hermes-ui`

Current upstream repo is a single-file HTML app with a Python stdlib server. Do not assume a Node/Vite build.

Launch path:

1. Clone the repo.
2. Run `serve_lite.py`, not `serve.py`.
3. Prefer the Hermes venv interpreter when available; `serve_lite.py` checks Python minor-version compatibility and re-execs into `~/.hermes/hermes-agent/venv/bin/python3` when needed.
4. Open `/hermes-ui.html`, not just `/`.
5. Verify with `/health`.

Example:

```bash
cd /path/to/hermes-ui
/home/you/.hermes/hermes-agent/venv/bin/python3 serve_lite.py --port 3333
# UI: http://127.0.0.1:3333/hermes-ui.html
# Health: http://127.0.0.1:3333/health
```

## Local discovery before cloning or launching alternatives

Before cloning a new workspace UI candidate, check whether the machine already has a usable Hermes web surface installed and whether a prior session recorded the launch path. This avoids redundant installs and helps recover the correct operator commands faster.

Recommended order:

1. Inspect likely local repos first.
   - Look for `hermes-webui`, `hermes-ui`, `dashboard`, or other Hermes-adjacent surface repos in the operator workspace.
2. If you find `hermes-webui`, check its daemon wrapper before assuming it is gone.
   - `./ctl.sh status`
   - `~/.hermes/webui.log`
   - `~/.hermes/webui.pid`
3. Treat stale PID files as untrusted until `ctl.sh status` confirms the process is actually running.
4. Only clone a different candidate after you confirm the existing surface is unusable or mismatched to the task.

## Pitfalls

- Root `/` may serve a directory listing instead of the app; use `/hermes-ui.html`.
- `serve.py` is only a deprecation shim; new launchers should target `serve_lite.py`.
- Do not waste time looking for `package.json` or a frontend build pipeline in this repo before checking the current upstream layout.
- Do not assume a previous Hermes web UI disappeared just because the HTTP port is closed; `hermes-webui` commonly leaves enough repo/log/PID state to recover the canonical launch path quickly.
- Do not trust `~/.hermes/webui.pid` by itself; validate with `./ctl.sh status`.
