# Exocórtex Home Layout — runtime Hermes vs workspace Exocórtex

## Decision

For new Hermes/Exocórtex instances:

```bash
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
EXOCORTEX_HOME="${EXOCORTEX_HOME:-$HOME/exocortex}"
ACERVO="${ACERVO:-$EXOCORTEX_HOME/acervo}"
```

Compatibility:

```text
~/.hermes/acervo -> ~/exocortex/acervo
```

The symlink preserves older skills/scripts. It is not the conceptual source of truth.

## Rationale

`~/.hermes` is Hermes control plane/runtime: `config.yaml`, `.env`, `auth.json`, `state.db`, sessions, logs, skills, profiles, Hindsight config, OAuth state and provider state.

The Exocórtex Acervo is cognitive/product scaffold. Keeping it inside the Hermes runtime couples product knowledge to engine state and makes broad file operations riskier.

`~/exocortex` is the better production workspace/cockpit. It gives the agent a meaningful cwd without exposing runtime internals as the default working tree.

## CWD rule

- CLI Hermes local uses the process launch directory.
- Gateway/messaging uses `terminal.cwd` in `config.yaml`.
- Production Exocórtex should prefer cwd at `$EXOCORTEX_HOME`.
- Avoid routine production sessions launched from `~/.hermes`; reserve that for explicit runtime maintenance.

## Refactor checklist

1. Setup script
   - introduce `EXOCORTEX_HOME` and `ACERVO`.
   - create `$EXOCORTEX_HOME/acervo`.
   - create `~/.hermes/acervo` symlink for compatibility.
   - require explicit flag for migrating a real legacy directory, e.g. `EXOCORTEX_MIGRATE_ACERVO=1`.

2. Acervo-resolving skills/scripts
   - `acervo-manager`.
   - `exocortex-new-microverso` and `scripts/create-microverso.sh`.
   - `exocortex-design-system`.
   - `personal-intake-workspace`.
   - `personal-artifact-workspace`.
   - `gerador-oficios`.
   - `docbrain-cli-api` docs/refs.

3. Tools stored in the Acervo
   - `global/tools/artifact_publish.py`.
   - `global/tools/intake_ingest.py`.

   Python resolver pattern:

   ```python
   def exocortex_home() -> Path:
       return Path(os.environ.get("EXOCORTEX_HOME", Path.home() / "exocortex")).expanduser()

   def acervo_root() -> Path:
       return Path(os.environ.get("ACERVO", exocortex_home() / "acervo")).expanduser()
   ```

   Keep `hermes_home()` only for runtime Hermes paths.

4. Templates and SOUL/profile files
   - `acervo_cognitivo` points to `~/exocortex/acervo/`.
   - `skills_dir` remains `~/.hermes/skills/exocortex/`.

5. Setup workflows
   - document `HERMES_HOME`, `EXOCORTEX_HOME`, and `ACERVO` separately.
   - Hindsight config remains `~/.hermes/hindsight/config.json`; templates live in the Acervo.

## Post-change audit

Validate:

- `$HERMES_HOME` exists and contains Hermes runtime.
- `$EXOCORTEX_HOME` exists.
- `$ACERVO` resolves to `$EXOCORTEX_HOME/acervo`.
- `~/.hermes/acervo` is symlink in new installs when present.
- intake/artifact/microverso tools write under `$ACERVO`.
- production `terminal.cwd` points to `$EXOCORTEX_HOME`.
- historical backups/logs are excluded from path-lint or marked legacy.

## Pitfalls

- Do not turn `HERMES_HOME` into workspace.
- Do not use `$HERMES_HOME/acervo` as canonical path in new skills.
- Do not rewrite historical logs/backups just to clear grep output.
- Do not move runtime config/auth/logs/sessions/provider state into `~/exocortex`.
