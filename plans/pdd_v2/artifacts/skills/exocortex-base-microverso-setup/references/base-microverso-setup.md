# Reference — Base microverses in replicable setup

This reference captures the reusable pattern from creating `estudio-criativo` as a base microverse of the Exocórtex/Hermes setup.

## When this applies

Use this pattern when a microverse represents a durable Exocórtex capability that should exist in new installations.

Examples:

- creative studio capability;
- intake workspace;
- artifact publishing workspace;
- setup/governance domain;
- reusable operational domain.

## Canonical sequence

1. Create the microverse in the Acervo with Ontology v2.
2. Keep its core generic and adaptive.
3. Add contracts that protect scope and behavior.
4. Add workflows/templates that make it operational.
5. Register the decision in `micro/hermes-setup`.
6. Update the replicable setup workflow.
7. Add or patch setup script only after Draft-First approval.
8. Validate both the real script and isolated provisioning.

## Files usually touched

```text
micro/{slug}/SCHEMA.md
micro/{slug}/index.md
micro/{slug}/log.md
micro/{slug}/contracts/*.md
micro/{slug}/workflows/*.md
micro/{slug}/templates/*.md
micro/{slug}/decisions/*.md

micro/hermes-setup/decisions/{slug}-base-microverso.md
micro/hermes-setup/workflows/replicable-exocortex-setup.md
micro/hermes-setup/index.md
micro/hermes-setup/log.md
shared/groups.md
~/.hermes/setup.sh
```

## Idempotent setup pattern

Use `mkdir -p` for directories. Use file existence guards for semantic files.

```bash
mkdir -p "$micro"/{context,knowledge,contracts,prompts,skills,workflows,tools,templates,decisions,reflections,persona,_meta,raw,_archive}

if [ ! -f "$micro/index.md" ]; then
  cat > "$micro/index.md" <<EOF
...
EOF
fi
```

## Heredoc rule

- Static content: `<<'EOF'`.
- Content with variables: `<<EOF`, but escape markdown backticks as `\``.

Failure mode: unescaped markdown backticks inside `<<EOF` run as shell command substitution. The shell may print `command not found` while still creating files, so syntax check alone is insufficient.

## Validation recipe

```bash
bash -n ~/.hermes/setup.sh

# Before applying a generated patch:
patch --dry-run target patchfile

# After adding a provision function, test it in isolation:
tmp_home=$(mktemp -d)
HERMES_HOME="$tmp_home" bash test-function-only.sh
HERMES_HOME="$tmp_home" bash test-function-only.sh
```

Assertions:

- required files exist;
- re-run preserves existing files;
- stderr is empty;
- markdown content contains intended backticks when expected;
- real `setup.sh` still passes `bash -n`.

## Draft-First note

Changes to setup scripts affect future environments. Present the patch as DRAFT with impact summary and wait for explicit approval before applying.
